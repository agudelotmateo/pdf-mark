### PDFMark
This app removes text watermarks from your PDF files! Now on Heroku: [give it a try!](http://pdf-mark.herokuapp.com/)

### Running locally

Just install the required dependencies from `requirements.txt` and run the application. Flask's own server is fine in this case. Using a *virtualenv* is recommended. Here's an example:

```
$ git clone https://github.com/agudelotmateo/pdf-mark.git
$ cd pdf-mark
$ python3 -m virtualenv venv-pdf-mark
$ source venv-pdf-mark/bin/source
$ python3 -m pip install -r requirements.txt
$ flask run
```

The app will now be running on `localhost:5000`. The `PORT` environment variable is not used with this method (so it doesn't neccesarily need to be set at this point). It's still possible to change both the host and the port Flask's server is run on by using the *host* and *port* flags. Here's an example:

```
$ flask run --host=0.0.0.0 --port=8080
```

And using this method it's also possible to use the `PORT` environment variable as well:

```
$ flask run --host=0.0.0.0 --port=$PORT
```

### Deployment to Heroku

Assuming the Heroku CLI is installed and you are already logged in:

```
$ git clone https://github.com/agudelotmateo/pdf-mark.git
$ cd pdf-mark
$ heroku container:login
$ heroku create
$ heroku container:push web
$ heroku container:release web
```

By now the app has already been deployed and can be opened by either using the assigned URL or running the following command:

```
$ heroku open
```

## Deployment explained

So the problem was getting a free server with Flask, Gunicorn and (especially) PDFTk installed in it. Then I thought about Docker and remembered that Heroku supports it. So all I needed to do know was to build the image, then the Dockerfile and finally the `docker-compose.yml`.

# Docker image

I started with a clean Ubuntu 16.04 which is the latest LTS to have PDFTk and it's dependencies ready to install from the main repositories. I also needed Python 3.6 which isn't as easy to install as on 18.04, but it wasn't as hard as installing PDFTk on 18.04. The rest of the dependencies are pretty much straight forward; this is the full list of commands ran on the container:

```
$ sudo apt update
$ apt install -y software-properties-common
$ add-apt-repository -y ppa:jonathonf/python-3.6
$ apt update
$ apt -y upgrade
$ apt install pdftk git python3.6 python3-pip -y
$ python3.6 -m pip install 'flask===1.0.2'
$ python3.6 -m pip install gunicorn
```

Notice that the flask installation (with the current state of this repository) could be changed to

```
$ python3 -m pip install -r requirements.txt
```

Now it was time to save it as an image:

```
$ docker commit -m "PDFMark-ready image" -a "potentialspecific" <container-id> potentialspecific/flask-pdftk
```

OK at this point with the image ready, it was time to actually create both the Dockerfile and the `docker-compose.yml`. Both are pretty straight forward and can be viewed here. The only things I think are worth mentioning are the use of the `PORT` environment variable which is required on Heroku and the enviroment variables that must be set inside of the container for Flask to properly execute the application (`FLASK_APP`, `LC_ALL` and `LANG`).

### Background

The following is an old story. As already mentioned, deployment is now being done using Docker and Heroku.

I recently found the need to remove a watermark from a PDF file I had because it was making the actual content of the file impossible to read.
What I found surprising is that the watermark was actually text, like most the other content in the file, so I thought that a simple find
and replace might do the trick. The search took me straight to the answer: YES, it will do the trick! But it's a little more complex than that:

- First, you need to uncompress the PDF file: just use PDFtk
- Now, you can do your "simple" find and replace: sed will do the job
- Finally, you need to recompress your PDF file back: PDFtk one more time

Now, that was easy to do locally. Of course it only works with text watermarks but its better than nothing (and clearly non-text watermarks require
much more advance techniques such as OCR or something like that). How do I do it programatically now, and run it on a server?

That's when the problems arrived. I never really thought of a bash script, but I knew that Python was able to run command-line programs. But this
imposed a problem: the dependencies (PDFtk in this case, sed is pretty much always there) must be available on the server. I forgot for some reason
about CS50's IDE and closed my mind to either Heroku (which integrated with a GitHub repository works awesome) or a traditional VPS which I really
didn't want to bother configuring. So I said to myself: pretty simple, just find yourself a Python library capable of performing the PDF uncompress
and compress steps... good luck with that because that library doesn't seem to exist. PDF's structure is very unstable and no libraries have been
developed using Python to perform this job (well, or maybe I am the only one who couldn't find them).

I was still reluctant about running PDFtk from Python, specially considering the need to setup the VPS and installing the dependencies (PDFtk is
particularly hard to install on Ubuntu 18.04 given its outdated dependencies), but then I remembered about CS50's IDE. Came in and installed
PDFtk in no time using apt with no problem at all and of course Flask works like charm. My choise became clear at this point.

### Implementation

## Back end
Its just Python with Flask (this is the only non-standard library required) on the programatic side, but also PDFtk and sed installed in the system.

Now, the only thing it does is processing one file at once on the `/remove` route by performing the three steps already described to remove text
watermarks from PDFs from python itself but calling the command line utilities mentioned previously.

## Front end
My knowledge about front end technologies is limited, but I know many free resources that I could use. I've always loved those fixed backgrounds
that stay put even if you scroll, and although there isn't much to scroll in this application, I still implemented it using an image from Unsplash.
Now a problem: my beautiful image was huge (a few megabytes) and it took ages for it to load, so I used ImageMagick to reduce the quality of the image
and blur it in order to lower its size. I used a script to automate the process in order to quickly try multiple images:

```python
import subprocess
import sys

infile = sys.argv[1]
outfile = sys.argv[2]
n = sys.argv[3]

params = ["convert", "-strip", "-interlace", "Plane", "-gaussian-blur", "0.05", "-quality", "50%", infile, outfile]
subprocess.call(params)

params = ["convert", "-scale", "50%", "-scale", "1000%", outfile, outfile]
subprocess.call(params)

params = ["convert", "-resize", f"{n}%", outfile, outfile]
subprocess.call(params)
```

Now, a small enough image to load almost instatly on my fairly limited connection was of very poor quality,
so I used a stronger blur effect using CSS only for the background, keeping the content on top of it clear.

Now the title and the form. The title was fairly easy to customize, although I had a problem in the order of my
"imports". The form was much more complex as my bootstrap knowledge is almost non existant, but I quickly found
Bootsnipp, a website with plenty of Bootstrap examples which made me more familiar with the syntax and led me
to learn the Bootstrap's grid system.

By now it was prettier and still working, but the gereral style didn't look as uniform as I expected. I finally
found ways to add arbitrary spaces, customize the buttons (even the file upload one, which is tricky) and, lastly,
adding shadows to the boxes. At this point it was pretty much ready.

Finally, I added a link to the GitHub repo with the code of the application and this awesome text. Made it using a nice
transparent centered button.

Aaaand last, but not least, added a favicon.

During all this time I was expecting to, in the end, modifiy the site to manage multiple files being uploaded and the same
time for batch processing. In the end, this proved to be kind of useless:

1. If I let the user upload multiple, it would be difficult to tell which watermark text to use with every file. Perhaps the same one but, who knows?
2. My original idea was using JS on a button to add more file/text pairs, but if we think about it this isn't much different from using the page multiple times

Maybe I will get a better idea (perhaps from user feedback?) in the future for this part and implement it. For now, this is it and it works flawlessly with
my university's certificates preview, from which I needed to remove the watermark in order to read my grades and at that specific moment my Linux VMs all failed
and it took me a lot of trouble to remove such watermark from Windows. That's the reason why I built this app: a more accessible way to perform this operation.
It doesn't always work though, PDF's inner contents are kinda messy but if your watermark can be selected as text, this app will most likely work!

### References

- [Linux - Find and replace string inside of PDF](https://stackoverflow.com/questions/9871585/how-to-find-and-replace-text-in-a-existing-pdf-file-with-pdftk-or-other-command)
- [Ubuntu - Installing Python 3.6 on 16.04](https://askubuntu.com/questions/865554/how-do-i-install-python-3-6-using-apt-get)
- [Flask - HTTP status codes](https://stackoverflow.com/questions/46805813/set-the-http-status-text-in-a-flask-response)
- [Flask - Uploading and downloading files](https://stackoverflow.com/questions/27628053/uploading-and-downloading-files-with-flask)
- [Flask - Uploading files](http://flask.pocoo.org/docs/1.0/patterns/fileuploads/)
- [Flask - Downloading files](https://stackoverflow.com/questions/41543951/how-to-change-downloading-name-in-flask)
- [Flask - Remove file after serving it](https://stackoverflow.com/questions/40853201/remove-file-after-flask-serves-it)
- [Flask - Favicon](http://flask.pocoo.org/docs/0.12/patterns/favicon/)
- [Flask - Running on production](https://stackoverflow.com/questions/41940663/why-cant-i-change-the-host-and-port-that-my-flask-app-runs-on)
- [Flask - Change server port](https://stackoverflow.com/questions/20212894/how-do-i-get-flask-to-run-on-port-80)
- [Python - Random string generation](https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python)
- [Python - Current date and time](https://www.cyberciti.biz/faq/howto-get-current-date-time-in-python/)
- [Python - Check if a directoy exists](https://stackoverflow.com/questions/8933237/how-to-find-if-directory-exists-in-python)
- [Python - Call external command](https://stackoverflow.com/questions/89228/calling-an-external-command-in-python)
- [Python - Reeturn value of subprocess.call](https://stackoverflow.com/questions/1696998/what-is-the-return-value-of-subprocess-call)
- [Python - Using sed](https://stackoverflow.com/questions/6706953/python-using-subprocess-to-call-sed)
- [Python - Extract filename from its path](https://stackoverflow.com/questions/8384737/extract-file-name-from-path-no-matter-what-the-os-path-format)
- [Python - Find index of last occurrence of string/char inside of another string](https://stackoverflow.com/questions/26443308/find-last-occurrence-of-character-in-string-python)
- [Python - Is it required to always close file handlers?](https://stackoverflow.com/questions/1832528/is-close-necessary-when-using-iterator-on-a-python-file-object)
- [CSS - Background-attachment Property](https://www.w3schools.com/CSSref/pr_background-attachment.asp)
- [CSS - Background-size Property](https://www.w3schools.com/cssref/css3_pr_background-size.asp)
- [CSS - Blur filter to background image](https://stackoverflow.com/questions/20039765/how-to-apply-a-css-3-blur-filter-to-a-background-image)
- [CSS - 20 Examples of Beautiful Typography Design](https://wdexplorer.com/20-examples-beautiful-css-typography-design/)
- [CSS - Knewave Font](https://fonts.google.com/specimen/Knewave?selection.family=Knewave)
- [ImageMagick](https://www.imagemagick.org/script/index.php)
- [ImageMagick - Pixelate image](https://stackoverflow.com/questions/331254/how-to-pixelate-blur-an-image-using-imagemagick)
- [ImageMagick - Recommendation for JPG compression](https://stackoverflow.com/questions/7261855/recommendation-for-compressing-jpg-files-with-imagemagick)
- [HTML - Button](https://www.w3schools.com/tags/tag_button.asp)
- [HTML - Button that acts like a link](https://stackoverflow.com/questions/2906582/how-to-create-an-html-button-that-acts-like-a-link)
- [HTML - Transparent buttons](https://stackoverflow.com/questions/22672368/how-to-make-a-transparent-html-button?answertab=active#tab-top)
- [HTML - Center buttons](https://stackoverflow.com/questions/4221263/center-form-submit-buttons-html-css)
- [Bootstrap - Registration form example](https://bootsnipp.com/snippets/featured/registration-form)
- [Bootstrap - Grid system](https://bootstrapdocs.com/v3.3.6/docs/css/#grid)
- [Bootstrap - Space between elements in row](https://stackoverflow.com/questions/10085723/twitter-bootstrap-add-top-space-between-rows)
- [Bootstrap - Buttons](https://www.w3schools.com/bootstrap/bootstrap_buttons.asp)
- [Bootstrap - Glyphicons](https://www.w3schools.com/bootstrap/bootstrap_glyphicons.asp)
- [Bootstrap - File upload button](https://stackoverflow.com/questions/11235206/twitter-bootstrap-form-file-element-upload-button)
- [Bootstrap - Box shadows](https://codepen.io/brandonhimpfen/pen/aOQaQw/)
- [Heroku - Docker Deploys](https://devcenter.heroku.com/articles/container-registry-and-runtime)
- [Heroku - Pushing containers](https://devcenter.heroku.com/articles/local-development-with-docker-compose)
- [Docker - Using Docker on Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04)
- [Image - Envelope, paper, colour and color HD photo by Joanna Kosinska on Unsplash](https://unsplash.com/photos/LAaSoL0LrYs)
- [Favicon - Free database favicon](https://www.freefavicon.com/freefavicons/software/iconinfo/database-1-152-28127.html)

