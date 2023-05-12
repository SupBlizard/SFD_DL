import os, sys, time, io
import json
import urllib.request, urllib.parse, urllib.error
from PIL import Image


# Rate limit can be changed to your liking. Keep in mind to not overload the servers
RATE_LIMIT = 0.1

# DO NOT CHANGE, THIS IS A CONSTANT
TILE_SIZE  = 500

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
    
    layer_url = f"https://img.superfreedraw.com/layers/1/layer_{layer_id}/tiles/0/"
    resolution = (abs(p[0]["x"] - p[1]["x"])*TILE_SIZE, abs(p[0]["y"] - p[1]["y"])*TILE_SIZE)
    outfile = f'{username} ({p[0]["x"]},{p[0]["y"]}) to ({p[1]["x"]},{p[1]["y"]}).png'

    # Print layer selection information
    print(f'Resolution: {res[0]}x{res[1]}')

    # Download tiles to tile directory
    download_tiles(layer_url, p, resolution, outfile)
    

def download_tiles(resolution, points, outfile):
    final = Image.new("RGBA", resolution)

    # todo: Loop through extra edge points
    for y in range(points[0]["y"], points[1]["y"]):
        for x in range(points[0]["x"], points[1]["x"]):
            try:
                url = layer_API + f"{serialise_zoom(x,y,0)}/{x}_{y}/{x}_{y}.png"
                tile = Image.open(io.BytesIO(urllib.request.urlopen(url).read()))
            except urllib.error.HTTPError as e:
                if e.code != 404: raise e
                tile = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), None)
                
            # Paste new tile onto final image
            final.paste(tile, get_offset(x, y, points))

            # Ratelimit requests
            time.sleep(RATE_LIMIT)
    
    # Save final render
    final.save(outfile, quality=100)


def get_offset(x,y,p):
    return (TILE_SIZE*(x-p[0]["x"]), TILE_SIZE*(y-p[0]["y"]))


def serialise_zoom(x,y,z):
    # todo: add zoom scalar
    return f"{int(x < 0)*-1}_{int(y < 0)*-1}"


def get_layer_from_username(username):
    with urllib.request.urlopen(f"https://www.superfreedraw.com/api/v1/getLayerByName/{username}") as resp:
        return json.loads(resp.read())["data"]["id"]


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