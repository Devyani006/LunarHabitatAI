import rasterio
import numpy as np

lbl_path = "data/AVGVISIB_75S_120M_201608.LBL"

with rasterio.open(lbl_path) as src:
    print("Driver:", src.driver)
    print("Width x Height (pixels):", src.width, "x", src.height)
    print("Number of bands:", src.count)
    print("Data type:", src.dtypes[0])
    print("Coordinate reference system (projection):", src.crs)
    print("Bounds (in projected meters):", src.bounds)
    print("Pixel size (resolution):", src.res)
    print("Scale factor:", src.scales)
    print("Offset:", src.offsets)

    data = src.read(1)
    print("\nArray shape:", data.shape)
    print("Min value:", np.nanmin(data))
    print("Max value:", np.nanmax(data))
    print("Mean value:", np.nanmean(data))
