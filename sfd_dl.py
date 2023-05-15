import sys, time, io, json, math
import urllib.request, urllib.error
from PIL import Image


# Rate limit can be changed to your liking. Please do not overload the servers
RATE_LIMIT = 0.1
TILE_SIZE  = 500

def main(username, p):
    get_user_layer = f"https://www.superfreedraw.com/api/v1/getLayerByName/{username}"
    layer_url = "https://img.superfreedraw.com/layers/1/layer_%s/tiles/"
    
    try:
        layer_url = layer_url % (json.loads(urllib.request.urlopen(get_user_layer).read())["data"]["id"])
    except urllib.error.URLError as e:
        raise ValueError(f"Error: Could not connect to the server: {e}")
    except urllib.error.HTTPError as e:
        raise ValueError(f"Error: User layer not found: {e}")
    
    outfile = f"{username} ({p[0]['x']},{p[0]['y']}) to ({p[1]['x']},{p[1]['y']}).png"
    resolution = (abs(p[0]["x"] - p[1]["x"])*TILE_SIZE, abs(p[0]["y"] - p[1]["y"])*TILE_SIZE)
    selection = str((p[1]['x']-p[0]['x'])*(p[1]['y']-p[0]['y']))

    # Print information
    print(f"Layer:      {username}")
    print(f"Resolution: {resolution[0]}x{resolution[1]}")
    print(f"Selection:  {selection} tiles \n")

    # Download tiles to tile directory and get filesize
    download_tiles(layer_url, resolution, selection, p, p.pop(2), outfile)
    print(f'\nFinished, saved at "./{outfile}"\n')
    


def download_tiles(layer_url, resolution, selection, p, z, outfile):
    final, count = (Image.new("RGBA", resolution), 0)
    start = time.perf_counter()

    # Loop through all tiles
    for y in range(p[0]["y"], p[1]["y"]):
        for x in range(p[0]["x"], p[1]["x"]):
            progress = f"[{str(count+1).zfill(len(selection))}/{selection}]: "
            try:
                q = (int(x < 0)*-1, int(y < 0)*-1)
                url = f"{z}/{q[0]}_{q[1]}/{x}_{y}/{x}_{y}.png"
                tile = Image.open(io.BytesIO(urllib.request.urlopen(layer_url + url).read()))
                progress += format_tile_url(x,y,z,q)
            except urllib.error.HTTPError as e:
                if e.code != 404: raise e
                tile = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), None)
                progress += "... 404 - Empty tile"

            # Paste new tile onto final image
            final.paste(tile, (TILE_SIZE*(x-p[0]["x"]), TILE_SIZE*(y-p[0]["y"])))
            
            # Print the progress
            print(progress)
            count += 1

            # Ratelimit requests
            time.sleep(RATE_LIMIT)
    
    # Save final render
    final.save(outfile, quality=100)


# Formatting
def format_tile_url(x,y,z,q):
    x, y = format_coordinate((x,y))
    q = format_coordinate(q)
    return f"... /tiles/{z}/{q[0]}_{q[1]}/{x}_{y}/{x}_{y}.png"

def format_coordinate(c):
    return [str(c[i]).rjust(len(str(c[i])) + (0 if c[i] < 0 else 1)," ") for i in range(len(c))]


def validate_params(argv):
    try:
        for i in range(1,5): argv[i] = int(argv[i])
    except ValueError:
        raise ValueError("Error: Coordinates must be integers")
    if len(argv) < 5:
        raise ValueError("Error: Start and End coordinates are required")
    if argv[1] > argv[3] or argv[2] > argv[4]:
        raise ValueError("Error: End coordinate must be bigger than the start (bottom right)")
    
    zoom = 0
    if len(argv) > 5:
        zoom = int(argv[5])
        if zoom > 7 or zoom < 0: raise ValueError("Error: Zoom can only go from 0 to 7 (0 is maximum quality)")


    return [
        {"x":math.floor(argv[1]/TILE_SIZE/2**zoom),"y":math.floor(argv[2]/TILE_SIZE/2**zoom)},
        {"x":math.floor(argv[3]/TILE_SIZE/2**zoom)+1,"y":math.floor(argv[4]/TILE_SIZE/2**zoom)+1},
        zoom
    ]


if __name__ == "__main__":
    try:
        if len(sys.argv) == 1:
            print("SFD_DL - A SuperFreeDraw Downloader\n")
            print("Usage: python sfd_dl.py [username] [start.x] [start.y] [end.x] [end.y] [zoom]")
        main(sys.argv[1], validate_params(sys.argv[1:]))
    except Exception as e:
        print(e, end="\n\n")
    except KeyboardInterrupt:
        print("\nAborting ....")