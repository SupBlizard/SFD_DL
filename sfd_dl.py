import sys, time, io, json, math
import urllib.request, urllib.error
from PIL import Image


# Rate limit can be changed to your liking. Please do not overload the servers
RATE_LIMIT = 0.1
TILE_SIZE  = 500

def main(username, p):
    get_user_layer = f"https://www.superfreedraw.com/api/v1/getLayerByName/{username}"
    layer_url = "https://img.superfreedraw.com/layers/1/layer_%s/tiles/0/"
    
    try:
        layer_url = layer_url % (json.loads(urllib.request.urlopen(get_user_layer).read())["data"]["id"])
    except urllib.error.URLError as e:
        print(f"Could not connect to the server: {e}")
        return 1
    except urllib.error.HTTPError as e:
        print(f"User layer not found: {e}")
        return 1
    
    outfile = f"{username} ({p[0]['x']},{p[0]['y']}) to ({p[1]['x']},{p[1]['y']}).png"
    resolution = (abs(p[0]["x"] - p[1]["x"])*TILE_SIZE, abs(p[0]["y"] - p[1]["y"])*TILE_SIZE)
    selection = str((p[1]['x']-p[0]['x'])*(p[1]['y']-p[0]['y']))

    # Print information
    print(f"Layer:      {username}")
    print(f"Resolution: {resolution[0]}x{resolution[1]}")
    print(f"Selection:  {selection} tiles \n")

    # Download tiles to tile directory and get filesize
    download_tiles(layer_url, resolution, selection, p, outfile)
    print(f'\nFinished, saved at "./{outfile}"\n')
    


def download_tiles(layer_url, resolution, selection, points, outfile):
    final, count = (Image.new("RGBA", resolution), 0)
    start = time.perf_counter()

    # Loop through all tiles
    for y in range(points[0]["y"], points[1]["y"]):
        for x in range(points[0]["x"], points[1]["x"]):
            progress = f"[{str(count+1).zfill(len(selection))}/{selection}]: "
            try:
                z = get_zoom(x,y,0)
                url = f"{z[0]}_{z[1]}/{x}_{y}/{x}_{y}.png"
                tile = Image.open(io.BytesIO(urllib.request.urlopen(layer_url + url).read()))
                print(progress, format_tile_url(x,y,z))
            except urllib.error.HTTPError as e:
                if e.code != 404: raise e
                tile = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), None)
                print(progress, "... 404 - Empty tile")

            # Paste new tile onto final image
            final.paste(tile, get_offset(x, y, points))
            count += 1

            # Ratelimit requests
            time.sleep(RATE_LIMIT)
    
    # Save final render
    final.save(outfile, quality=100)


def format_tile_url(x,y,z):
    x, y = format_coord((x,y))
    z = format_coord(z)
    return f"... /{z[0]}_{z[1]}/{x}_{y}/{x}_{y}.png"


def format_coord(c):
    return [str(c[i]).rjust(len(str(c[i])) + (0 if c[i] < 0 else 1)," ") for i in range(len(c))]


def get_offset(x,y,p):
    return (TILE_SIZE*(x-p[0]["x"]), TILE_SIZE*(y-p[0]["y"]))


def get_zoom(x,y,z):
    # todo: add zoom scalar
    return (int(x < 0)*-1, int(y < 0)*-1)


def validate_params(argv):
    try:
        for i in range(1,5): argv[i] = int(argv[i])
    except ValueError:
        raise ValueError("Error: coordinates must be integers")

    if len(argv) < 5:
        raise ValueError("Usage: python sfd_dl [username] [start.x] [start.y] [end.x] [end.y] \n\n"+
        "Example: python sfd_dl uncat -5 -10 3 -1")
    if argv[1] > argv[3] or argv[2] > argv[4]:
        raise ValueError("Error: end coordinate must be bigger than the start (bottom right)")

    return [
        {"x":math.ceil(argv[1]/(TILE_SIZE)),"y":math.ceil(argv[2]/(TILE_SIZE))},
        {"x":math.ceil(argv[3]/(TILE_SIZE)),"y":math.ceil(argv[4]/(TILE_SIZE))}
    ]


if __name__ == "__main__":
    try:
        main(sys.argv[1], validate_params(sys.argv[1:]))
    except Exception as e:
        print(e, end="\n\n")
        raise e
    except KeyboardInterrupt:
        print("\nAborting ....")