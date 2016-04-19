import os
import re
import shutil
import zipfile
from StringIO import StringIO

import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from . import get_locale_path
from . import make_dir


@csrf_exempt
def hook(request):
    file_name = request.POST.get('file')

    if file_name:
        r = requests.get('https://lokali.se/{0}'.format(file_name))
        if r.status_code == 200:
            locale_path = get_locale_path()

            f = StringIO(r.content)

            if os.access(locale_path, os.W_OK | os.X_OK):
                with zipfile.ZipFile(f) as zip_file:
                    for member in zip_file.namelist():
                        filename = os.path.basename(member)
                        if not filename:
                            continue

                        if re.search(r"\.po$", filename):
                            [lang, ext] = os.path.splitext(filename)

                            lang_path = os.path.join(os.path.join(locale_path, lang), 'LC_MESSAGES')
                            make_dir(lang_path)

                            source = zip_file.open(member)
                            target = file(os.path.join(lang_path, "django.{0}".format(ext)), "wb")
                            with source, target:
                                shutil.copyfileobj(source, target)

    return HttpResponse('')