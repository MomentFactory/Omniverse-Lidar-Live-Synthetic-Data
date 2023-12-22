#include <OgnBeamToOusterUDPNodeDatabase.h>

#include <chrono>

#define WIN32_LEAN_AND_MEAN
#define _WINSOCK_DEPRECATED_NO_WARNINGS
#ifdef _WIN32
#include <Winsock2.h>
#else
#include <arpa/inet.h>
#include <netdb.h>
#include <netinet/in.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <sys/types.h>
#define SOCKET int
#define INVALID_SOCKET  (SOCKET)(~0)
#define SOCKET_ERROR            (-1)
#define closesocket close
#define SOCKADDR sockaddr
#endif


namespace mf {
namespace ov {
namespace lidar_live_synth {

static const int kColumnsPerPacket = 16;
static const float kPi = 3.14159265359f;
static const float kTwoPi = kPi * 2.0f;
static const float kDegToRad = kTwoPi / 360.0f;
static const int kOusterNumRotAngles = 90112;
static const float kOusterNumRotAnglesOverTwoPi = kOusterNumRotAngles / kTwoPi;

class OgnBeamToOusterUDPNode
{
    int m_frameId{ 0 };

#pragma pack(push,4) // Force packing in 4-byte packs (Words)

    struct OusterChannelDataBlock
    {
        unsigned int rangemm;
        unsigned short reflectivity;
        unsigned short signal_photons;
        unsigned short noise_photons;
        unsigned short unused;

        OusterChannelDataBlock()
            : rangemm(0)
            , reflectivity(0)
            , signal_photons(0)
            , noise_photons(0)
            , unused(0)
        {}
    };

    template <int NUMROWS>
    struct OusterAzimuthBlock
    {
        unsigned long long timeStamp;					  // Word 0,1
        unsigned short measurementId;					  // Word 2[0:15]
        unsigned short frameId;							  // Word 2[16:31]
        unsigned int encoderCount;						  // Word 3
        OusterChannelDataBlock channelDataBlock[NUMROWS]; // Word [4:195] in groups of 3
        unsigned int azimuthDataBlockStatus;			  // word 196

        OusterAzimuthBlock()
            : timeStamp(0)
            , measurementId(0)
            , frameId(0)
            , encoderCount(0)
            , channelDataBlock{}
            , azimuthDataBlockStatus(0)
        {}
    };

    template <int NUMROWS>
    struct OusterDataPacket
    {
        OusterAzimuthBlock<NUMROWS> block[16]; // Each packet consists of 16 azimuth blocks

        OusterDataPacket()
            :block{}
        {}
    };

#pragma pack(pop)


    class OgnBeamToOusterUDPNodeSocket
    {
    public:
        OgnBeamToOusterUDPNodeSocket()
            : SendSocket(INVALID_SOCKET)
            , isBroadcastSocket(false)
        {}

        virtual ~OgnBeamToOusterUDPNodeSocket()
        {
            if (SendSocket != INVALID_SOCKET)
            {
                closesocket(SendSocket);
            }
        }

        bool prepare(OgnBeamToOusterUDPNodeDatabase& db)
        {
            if (isBroadcastSocket != db.inputs.broadcast())
            {
                closesocket(SendSocket);
                SendSocket = INVALID_SOCKET;
            }

            if (SendSocket == INVALID_SOCKET)
            {
                SendSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);

                if (SendSocket == INVALID_SOCKET)
                {
                    db.logError("Error in OgnBeamToOusterUDPNode opening socket : %d", SendSocket);
                    return false;
                }

                if (db.inputs.broadcast())
                {
                    char broadcast = 1;
                    int iResult = setsockopt(SendSocket, SOL_SOCKET, SO_BROADCAST, &broadcast, sizeof(broadcast));
                    if (!iResult)
                    {
                        closesocket(SendSocket);
                        SendSocket = INVALID_SOCKET;

                        db.logError("Error in OgnBeamToOusterUDPNode setting socket options : %d", iResult);
                        return false;
                    }
                }

                isBroadcastSocket = db.inputs.broadcast();
            }

            RecvAddr.sin_family = AF_INET;
            RecvAddr.sin_port = htons(db.inputs.port());
            std::string ipAddress = db.inputs.ip_address();
            RecvAddr.sin_addr.s_addr = inet_addr(ipAddress.data());

            return true;
        }

        template <int NUMROWS>
        bool send(const OusterDataPacket<NUMROWS>& packet, OgnBeamToOusterUDPNodeDatabase& db)
        {
            int iResult = sendto(SendSocket, reinterpret_cast<const char*>(&packet), sizeof(packet), 0, (SOCKADDR*)&RecvAddr, sizeof(RecvAddr));
            if (iResult == SOCKET_ERROR)
            {
                db.logError("Error in OgnBeamToOusterUDPNode sending data on socket : %d", iResult);

                return false;
            }

            return true;
        }
    private:
        SOCKET SendSocket;
        sockaddr_in RecvAddr;
        bool isBroadcastSocket;
    };

    OgnBeamToOusterUDPNodeSocket m_ognBeamToOusterUDPNodeSocket;

    template<int NUMROWS>
    static bool computeForSize(OgnBeamToOusterUDPNodeDatabase& db)
    {
        auto& state = db.internalState<OgnBeamToOusterUDPNode>();

        const auto& linearDepthData = db.inputs.linearDepthData();
        const int& numCols = db.inputs.numCols();
        const float& azimuthStart = db.inputs.azimuthRange()[0] + kTwoPi + kTwoPi;
        const float& horizontalStepInRads = -1.0f * db.inputs.horizontalResolution() * kDegToRad;
        const int& frameId = state.m_frameId % 65536;

        try
        {
            if (!state.m_ognBeamToOusterUDPNodeSocket.prepare(db))
            {
                return false;
            }

            int measurementId = 0;

            OusterDataPacket<NUMROWS> packet;
            int currentChunkColumn = 0;

            // We need to send data in ascending angle (encoder_count) order
            // Data is in right-to-left order, we need to iterate left-to-right
            // We also need to start at the middle (center) of the data which is encoderCount 0
            int colEndIndex = (numCols - 1) / 2;
            int colStartIndex = colEndIndex + numCols;

            for (int tempColIndex = colStartIndex; tempColIndex > colEndIndex; tempColIndex--)
            {
                int colIndex = tempColIndex % numCols;

                // This assumes consistent input data across azimuthRange, horizontalResolution, numCols, numRows and linearDepthData size
                int currentEncoderCount = int((azimuthStart + horizontalStepInRads * tempColIndex) * kOusterNumRotAnglesOverTwoPi);
                if (currentEncoderCount < 0 || currentEncoderCount >= kOusterNumRotAngles)
                {
                    db.logError("currentEncoderCount must be between 0 and %d, not %d", kOusterNumRotAngles, currentEncoderCount);
                    return false;
                }

                // If previous chunk is complete, start new one
                if (currentChunkColumn == kColumnsPerPacket)
                {
                    state.m_ognBeamToOusterUDPNodeSocket.send<NUMROWS>(packet, db);
                    packet = OusterDataPacket<NUMROWS>();

                    currentChunkColumn = 0;
                }

                packet.block[currentChunkColumn].timeStamp =
                    std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
                packet.block[currentChunkColumn].measurementId = measurementId;
                packet.block[currentChunkColumn].frameId = frameId;
                packet.block[currentChunkColumn].encoderCount = currentEncoderCount;

                measurementId = (measurementId + 1) % 65536;
                int colIndexStart = colIndex * NUMROWS;

                for (int rowIndex = 0; rowIndex < NUMROWS; rowIndex++)
                {
                    packet.block[currentChunkColumn].channelDataBlock[rowIndex].rangemm = (int)(linearDepthData[colIndexStart + rowIndex] * 1000.0f);
                    packet.block[currentChunkColumn].channelDataBlock[rowIndex].signal_photons = 0xFFFF; //0xFFFF means valid
                }

                packet.block[currentChunkColumn].azimuthDataBlockStatus = 0xFFFFFFFF; //0xFFFFFFFF means valid

                currentChunkColumn++;
            }

            if (currentChunkColumn != 0)
            {
                for (int extraColumnIndex = currentChunkColumn; extraColumnIndex < kColumnsPerPacket; extraColumnIndex++)
                {
                    packet.block[extraColumnIndex].timeStamp =
                        std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
                    packet.block[extraColumnIndex].measurementId = measurementId;
                    packet.block[extraColumnIndex].frameId = frameId;
                    packet.block[extraColumnIndex].encoderCount = kOusterNumRotAngles;
                }

                state.m_ognBeamToOusterUDPNodeSocket.send<NUMROWS>(packet, db);
            }

        }
        catch (...)
        {
            db.logError("Error in OgnBeamToOusterUDPNode::compute");
            return false;

        }

        state.m_frameId++;

        // Always enable the output execution
        db.outputs.execOut() = omni::graph::core::ExecutionAttributeState::kExecutionAttributeStateEnabled;

        // Even if inputs were edge cases like empty arrays, correct outputs mean success
        return true;
    }

public:
    static bool compute(OgnBeamToOusterUDPNodeDatabase& db)
    {
        // TODO: why is state declared here
        // auto& state = db.internalState<OgnBeamToOusterUDPNode>();
        const int& numRows = db.inputs.numRows();

        switch (numRows)
        {
        case 16:
            return computeForSize<16>(db);
            break;
        case 32:
            return computeForSize<32>(db);
            break;
        case 64:
            return computeForSize<64>(db);
            break;
        case 128:
            return computeForSize<128>(db);
            break;
        }

        db.logError("Row count must be either 16, 32, 64 or 128, not %d", numRows);
        return false;
    }
};

// This macro provides the information necessary to OmniGraph that lets it automatically register and deregister
// your node type definition.
REGISTER_OGN_NODE()

}
}
}
