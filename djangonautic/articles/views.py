from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Article
from django.contrib.auth.decorators import login_required
from . import forms
import os
from pyreportjasper import JasperPy
import subprocess


def compiling():
    input_file = os.path.dirname(os.path.abspath(__file__)) + '/prueba_Template.jrxml'
    jasper = JasperPy()
    jasper.compile(input_file)


def generar_reporte(request):
    compiling()
    input_file = os.path.dirname(os.path.abspath(__file__)) + '/prueba_Template.jrxml'
    output = os.path.dirname(os.path.abspath(__file__)) + '/reporte'
    pdfFile = os.path.dirname(os.path.abspath(__file__)) + '/reporte.pdf'
    con = {
        'driver': 'postgres',
        'username': 'postgres',
        'password': 'freyser',
        'host': 'localhost',
        'database': 'blognautic',
        'schema': 'public',
        'port': '5432'
    }
    print(con)
    jasper = JasperPy()
    jasper.process(
        input_file,
        output_file=output,
        format_list=["pdf"],
        parameters={},
        db_connection=con,
        locale='en_US'  # LOCALE Ex.:(en_US, de_GE)
    )
    subprocess.Popen(pdfFile, shell=True)
    return render(request, 'articles/article_list.html')


def article_list(request):
    articles = Article.objects.all().order_by('date')
    return render(request, 'articles/article_list.html', {'articles': articles})


def article_detail(request, slug):
    article = Article.objects.get(slug=slug)
    return render(request, 'articles/article_detail.html', {'article': article})


@login_required(login_url="/accounts/login/")
def article_create(request):
    if request.method == 'POST':
        form = forms.CreateArticle(request.POST, request.FILES)
        if form.is_valid():
            # save article to db
            instance = form.save(commit=False)
            instance.author = request.user
            instance.save()
            return redirect('articles:list')
    else:
        form = forms.CreateArticle()
    return render(request, 'articles/article_create.html', {'form': form})
