import os, sys, time, io, json
import urllib.request, urllib.parse, urllib.error
from PIL import Image


# Rate limit can be changed to your liking. Keep in mind to not overload the servers
RATE_LIMIT = 0.1
TILE_SIZE    = 500

def main(username, p):
    try:
        layer_id = get_layer_from_username(username)
    except urllib.error.URLError as e:
        print(f"Could not connect to the server: {e}")
        return 1
    except urllib.error.HTTPError as e:
        print(f"User layer not found: {e}")
        return 1
    
    layer_url = f"https://img.superfreedraw.com/layers/1/layer_{layer_id}/tiles/0/"
    outfile = f"{username} ({p[0]['x']},{p[0]['y']}) to ({p[1]['x']},{p[1]['y']}).png"
    resolution = (abs(p[0]["x"] - p[1]["x"])*TILE_SIZE, abs(p[0]["y"] - p[1]["y"])*TILE_SIZE)
    selection = str((p[1]['x']-p[0]['x'])*(p[1]['y']-p[0]['y']))

    # Print information
    print(f"Layer ID:   {layer_id} ({username})")
    print(f"Resolution: {resolution[0]}x{resolution[1]}")
    print(f"Selection:  {selection} tiles \n")

    # Download tiles to tile directory and get filesize
    download_tiles(layer_url, resolution, selection, p, outfile)

    print(f'\nFinished, saved at "./{outfile}"\n')
    

def download_tiles(layer_url, resolution, selection, points, outfile):
    final, count = (Image.new("RGBA", resolution), 0)

    for y in range(points[0]["y"], points[1]["y"]):
        for x in range(points[0]["x"], points[1]["x"]):
            print(f"[{str(count).zfill(len(selection))}/{selection}]: ", end="")
            try:
                url = f"{serialise_zoom(x,y,0)}/{x}_{y}/{x}_{y}.png"
                tile = Image.open(io.BytesIO(urllib.request.urlopen(layer_url + url).read()))
                print(format_tile_url(url))
            except urllib.error.HTTPError as e:
                if e.code != 404: raise e
                tile = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), None)
                print("Empty tile, skipping")
                
            # Paste new tile onto final image
            final.paste(tile, get_offset(x, y, points))
            count += 1

            # Ratelimit requests
            time.sleep(RATE_LIMIT)
    
    # Save final render
    final.save(outfile, quality=100)


def format_tile_url(url):
    url = url.split("/")
    return f"{url[0].rjust(5,' ')}/{url[1].rjust(5,' ')}/{url[2].rjust(9,' ')}"


def get_offset(x,y,p):
    return (TILE_SIZE*(x-p[0]["x"]), TILE_SIZE*(y-p[0]["y"]))


def serialise_zoom(x,y,z):
    # todo: add zoom scalar
    return f"{int(x < 0)*-1}_{int(y < 0)*-1}"


def get_layer_from_username(username):
    with urllib.request.urlopen(f"https://www.superfreedraw.com/api/v1/getLayerByName/{username}") as resp:
        return json.loads(resp.read())["data"]["id"]


def validate_params(argv):
    try:
        for i in range(1,5): argv[i] = int(argv[i])
    except ValueError:
        raise ValueError("Error: coordinates must be integers")

    if len(argv) < 5:
        raise ValueError("Usage: python sfd_dl [username] [start.x] [start.y] [end.x] [end.y] \n\n"+
        "Example: python sfd_dl uncat -5 -10 3 -1")
    if argv[1] > argv[3] or argv[2] > argv[4]:
        raise ValueError("Error: end point axis must be bigger than start point")

    return [{"x":argv[1],"y":argv[2]},{"x":argv[3],"y":argv[4]}]


if __name__ == "__main__":
    try:
        main(sys.argv[1], validate_params(sys.argv[1:]))
    except Exception as e:
        print(e, end="\n\n")