import os, sys, time
import json
import urllib.request, urllib.parse, urllib.error
from PIL import Image


TILE_SIZE  = 500
RATE_LIMIT = 0.1


def main(username, points):
    try:
        layer_id = get_layer_from_username(username)
        print(layer_id)
    except urllib.error.URLError as e:
        print(f"Could not connect to the server: {e}")
        return 1
    except urllib.error.HTTPError as e:
        print(f"User layer not found: {e}")
        return 1

    # Create temp tile directory
    if not os.path.exists("tiles"):
        os.makedirs("tiles")
    
    # Download tiles to tile directory
    download_tiles(layer_id, points)



# Get layer ID
def get_layer_from_username(username):
    with urllib.request.urlopen(f"https://www.superfreedraw.com/api/v1/getLayerByName/{username}") as resp:
        return json.loads(resp.read())["data"]["id"]


# Download tiles between the two points
def download_tiles(id, p):
    layer_API = f"https://img.superfreedraw.com/layers/1/layer_{id}/tiles/0/"
    for y in range(p[0]["y"], p[1]["y"]):
        for x in range(p[0]["x"], p[1]["x"]):
            filename = f"tiles/Tile_Y{y-p[0]['y']}_X{x-p[0]['x']}.png"
            if os.path.isfile(filename): continue

            try:
                url = layer_API + f"{int(x < 0)*-1}_{int(y < 0)*-1}/{x}_{y}/{x}_{y}.png"
                urllib.request.urlretrieve(url,filename)
            except urllib.error.HTTPError as e:
                if e.code != 404: raise e

                # Save blank tile
                Image.new("RGBA", (TILE_SIZE, TILE_SIZE), None).save(filename, "PNG")
            
            # Re-encode tile
            Image.open(filename).convert("RGBA").save(filename, "PNG")

            # Ratelimit requests
            time.sleep(RATE_LIMIT)


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