import json
import os
import uuid

from cookiecutter.main import cookiecutter
import requests
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
import shutil

from cookiecutter_wizard_app.cookie_template_allow_list import ALLOWED_COOKIECUTTER_TEMPLATES

COOKIECUTTER_JSON_URL_TEMPLATE = "https://raw.githubusercontent.com/{}/main/cookiecutter.json"


def config_json_url_from_template_name(template_name):
    # remove 'gh:'
    user_slash_repo = template_name[3:]
    return COOKIECUTTER_JSON_URL_TEMPLATE.format(user_slash_repo)


# Create your views here.
class CookieCutterView(View):
    def get(self, request):
        cookiecutter_template = request.GET.get("template", None)

        if cookiecutter_template is None:
            return HttpResponse('Error: Must specify template')

        if cookiecutter_template not in ALLOWED_COOKIECUTTER_TEMPLATES:
            return HttpResponse('Error: Invalid cookiecutter template')

        conf_json_resp = requests.get(config_json_url_from_template_name(cookiecutter_template))
        template_conf_obj = conf_json_resp.json()

        return render(request, "cookiecutter_wizard.html",
                      {"template_conf_obj": template_conf_obj})

    def post(self, request):
        cookiecutter_values = {}
        cookiecutter_template = request.GET.get("template", None)
        for post_arg in request.POST:
            if post_arg != "csrfmiddlewaretoken":
                # print(post_arg)
                cookiecutter_values[post_arg] = request.POST[post_arg]

        tmp_filename = f"tmp_{uuid.uuid4()}.json"

        tmp_filepath = f"cookiecutter_wizard_app/cookie_kitchen/{tmp_filename}"

        project_dir_fullpath = cookiecutter(cookiecutter_template,
                                            extra_context=cookiecutter_values,
                                            output_dir="cookiecutter_wizard_app/cookie_kitchen/",
                                            no_input=True)

        project_dir = project_dir_fullpath.split("/")[-1]

        shutil.make_archive(f"media/generated/{project_dir}", 'zip', project_dir_fullpath)

        shutil.rmtree(project_dir_fullpath)

        project_zip_url = f"/media/generated/{project_dir}.zip"
        return render(request, "post_gen.html", {
            "project_zip_url": project_zip_url
        })


class IndexView(View):
    def get(self, request):
        return HttpResponse('Hello, cookiecutter!')
