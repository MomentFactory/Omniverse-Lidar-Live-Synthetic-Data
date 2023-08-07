#define CARB_EXPORTS

#include <carb/PluginUtils.h>

#include <omni/ext/IExt.h>
#include <omni/graph/core/IGraphRegistry.h>
#include <omni/graph/core/ogn/Database.h>
#include <omni/graph/core/ogn/Registration.h>

// Standard plugin definitions required by Carbonite.
const struct carb::PluginImplDesc pluginImplDesc = { "mf.ov.lidar_live_synth.plugin",
                                                     "MF Lidar live synthetic data.", "MF",
                                                     carb::PluginHotReload::eEnabled, "dev" };

// These interface dependencies are required by all OmniGraph node types
CARB_PLUGIN_IMPL_DEPS(omni::graph::core::IGraphRegistry,
                      carb::flatcache::IPath,
                      carb::flatcache::IToken)

// This macro sets up the information required to register your node type definitions with OmniGraph
DECLARE_OGN_NODES()

namespace mf
{
namespace ov
{
namespace lidar_live_synth
{

class LidarLiveSyntheticDataExtension : public omni::ext::IExt
{
public:
    void onStartup(const char* extId) override
    {
        // This macro walks the list of pending node type definitions and registers them with OmniGraph
        INITIALIZE_OGN_NODES()
    }

    void onShutdown() override
    {
        // This macro walks the list of registered node type definitions and deregisters all of them. This is required
        // for hot reload to work.
        RELEASE_OGN_NODES()
    }

private:
};

}
}
}

CARB_PLUGIN_IMPL(pluginImplDesc, mf::ov::lidar_live_synth::LidarLiveSyntheticDataExtension)

void fillInterface(mf::ov::lidar_live_synth::LidarLiveSyntheticDataExtension& iface)
{
}
