import os, sys, time, io
import json
import urllib.request, urllib.parse, urllib.error
from PIL import Image


TILE_SIZE  = 500
RATE_LIMIT = 0.1


def main(username, p):
    try:
        layer_id = get_layer_from_username(username)
        print(layer_id)
    except urllib.error.URLError as e:
        print(f"Could not connect to the server: {e}")
        return 1
    except urllib.error.HTTPError as e:
        print(f"User layer not found: {e}")
        return 1
    
    # Download tiles to tile directory
    outfile = f'{username} ({p[0]["x"]},{p[0]["y"]}) to ({p[1]["x"]},{p[1]["y"]}).png'
    download_tiles(layer_id, p, outfile)
    

# Get layer ID
def get_layer_from_username(username):
    with urllib.request.urlopen(f"https://www.superfreedraw.com/api/v1/getLayerByName/{username}") as resp:
        return json.loads(resp.read())["data"]["id"]


# Download tiles between the two points
def download_tiles(id, p, outfile):
    layer_API = f"https://img.superfreedraw.com/layers/1/layer_{id}/tiles/0/"
    res = (abs(p[0]["x"] - p[1]["x"])*TILE_SIZE, abs(p[0]["y"] - p[1]["y"])*TILE_SIZE)
    print(f'Resolution: {res[0]}x{res[1]}')

    final = Image.new("RGBA", (res[0], res[1]))

    # todo: Loop through extra edge points
    for y in range(p[0]["y"], p[1]["y"]):
        for x in range(p[0]["x"], p[1]["x"]):
            tile = None
            try:
                url = layer_API + f"{int(x < 0)*-1}_{int(y < 0)*-1}/{x}_{y}/{x}_{y}.png"
                with urllib.request.urlopen(url) as resp:
                    tile = Image.open(io.BytesIO(resp.read()))
            except urllib.error.HTTPError as e:
                if e.code != 404: raise e
                tile = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), None)
                
            # Paste new tile onto final image
            final.paste(tile, (TILE_SIZE*(x-p[0]["x"]), TILE_SIZE*(y-p[0]["y"])))

            # Ratelimit requests
            time.sleep(RATE_LIMIT)
    
    # Save final render
    final.save(outfile, quality=100)


# Validate user parameters
def validate_params(argv):
    for i in range(1,5):
        argv[i] = int(argv[i])

    if len(argv) < 5:
        raise ValueError("Usage: python sfd_dl [username] [start.x] [start.y] [end.x] [end.y] \n\n"+
        "Example: python sfd_dl uncat -5 -10 3 -1")
    if argv[1] > argv[3] or argv[2] > argv[4]:
        raise ValueError("Error: end point axis must be bigger than start point")

    return [{"x":argv[1],"y":argv[2]},{"x":argv[3],"y":argv[4]}]


if __name__ == "__main__":
    main(sys.argv[1], validate_params(sys.argv[1:])) 