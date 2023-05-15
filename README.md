# SuperFreeDraw DL
This is a basic utility tool for downloading tiles stored on [superfreedraw.com](superfreedraw.com) and stiching them together into a single final image for your own use.

I made this because I wanted to download my own layer but the service did not provide any way for users to download their own stuff which annoyed me a bit. So I ended up finding out how the website worked and got to work on this small program !

<br>

## How to use it

This program has the following arguments:

`python sfd_dl.py [username] [start.x] [start.y] [end.x] [end.y] [zoom]`

- Username -
The username of the layer owner as it apears on the URL.

- Start -> End - 
This is where you put the start coordinate and the end coordinate. You can find
the coordinates by positioning your screen so the point you want is in the center and then looking at the bottom left corner of the website (it tells you the coordinate).

- Zoom -
Zoom is optional as it is 0 by default. In this case 0 is actually a 1:1 picture of your selection while 7 is the maximum you can zoom out (2^7 being 128 or 1:128 as it says on the website)


### Example
If we look around [this layer](https://www.superfreedraw.com/wirisuzret4rn) for example
![A layer selection](https://raw.githubusercontent.com/SupBlizard/SFD_DL/main/screenshots/example.png)
If we decide that we want to get all of the tiles from `(-1900,-2000)` to `(950,-50)` then we can just type:

`python sfd_dl.py wirisuzret4rn -1900 -2000 950 -50`

It is not nessesary to enter anything for zoom as you probably want a 1:1 download of the tiles 90% of the tiles. But if you do want a more lower quality picture you can set the zoom argument up until 7.

<br>

While the program runs you should see something like this:

![The program log](https://raw.githubusercontent.com/SupBlizard/SFD_DL/main/screenshots/log-example.png)

And after it finishes you should have the final picture in the same directory as the program !

(The coordinates in the file are tile coordinates not pixel coordinates)

![Result](https://raw.githubusercontent.com/SupBlizard/SFD_DL/main/screenshots/final-example.png)


*Credit to* ***wirisuzret4rn*** *for letting me use his awesome layer as an example*


<br>

## Things to keep in mind
- The final image will not start and end exactly at the coordinates you chose as it is just a stiched version of all of the 500x500 tiles inbetween the coordinates.

- The axis of the start coordinate must be smaller than the end coordinate (this just means that the end coordinate must be bottom right of the start coordinate)

- There is a default ratelimit of 0.1 seconds. This means that the program will wait a bit after every request in order to not overload the server. This constant can be changed but keep in mind that too many requests could harm the server and could be a form of DOS so keeping it between 0.1 and 0.05 is recommended.

<br>

## Bugs
If you find any bugs or have any questions please send me a message at `SupBlizard#3813` on discord or write an issue and I will look into it. Keep in mind that this is a very basic program and that I didn't work on it for that long.