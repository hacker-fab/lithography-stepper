# %%
from harvesters.core import Harvester

# %%
import numpy as np
h = Harvester()
h.add_file('/opt/spinnaker/lib/flir-gentl/FLIR_GenTL.cti')
h.update()

# %%
h.device_info_list
# %%
ia = h.create()
# ia.remote_device.node_map.Width.value = 1796
# ia.remote_device.node_map.Height.value = 884
# ia.remote_device.node_map.PixelFormat.value = 'Mono8'
# %%
ia.remote_device.node_map.MaxWidth
# %%
