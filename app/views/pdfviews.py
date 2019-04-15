"""
Definition of PDF views.
"""

import os, io

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.http import HttpResponse
from django_xhtml2pdf.utils import generate_pdf
from django.contrib.auth import context_processors

from PyPDF2 import PdfFileMerger

from app.models import Proposals, Status

class PdfResponseMixin(object, ):
    def write_pdf(self, file_object, pagenumber = None):
        context = self.get_context_data()
        context["page"] = pagenumber
        template = self.get_template_names()[0]
        generate_pdf(template, file_object=file_object, context=context)

    def render_to_response(self, context, **response_kwargs):
        resp = HttpResponse(content_type='application/pdf')
        self.write_pdf(resp)
        return resp
        

class FullPdfResponseMixin(PdfResponseMixin, ):
    scibg = None
    
    def render_to_response(self, context, **response_kwargs):
        merger = PdfFileMerger()
        
        pdf_fo = io.BytesIO()
        self.write_pdf(pdf_fo, pagenumber=1)
        merger.append(pdf_fo)

        if context["object"].scientific_bg:
            filepath = os.path.join(settings.BASE_DIR,context["object"].scientific_bg.url[1:])
            merger.append(open(filepath, "rb"))
        
        pdf_lo = io.BytesIO()
        self.write_pdf(pdf_lo, pagenumber=2)
        merger.append(pdf_lo)

        resp = HttpResponse(content_type='application/pdf')
        merger.write(resp)
        return resp



class ProposalPdfDetailView(FullPdfResponseMixin, DetailView):
    template_name = "pdf/proposal_cover.html"
    context_object_name = 'proposal'
    model = Proposals

    def get_object(self):
        return get_object_or_404(Proposals, pid=self.kwargs["pid"])

    def get_context_data(self, *args, **kwargs):
        context = super(ProposalPdfDetailView, self).get_context_data(*args, **kwargs)
        context['status_history'] = Status.objects.filter(proposal=self.object).exclude(status__in="UR")
        try:
            context['tech'] = Status.objects.filter(proposal=self.object).filter(status="W").latest('date')
        except Status.DoesNotExist:
            context['tech'] = None
        
        
        context = {**context, **context_processors.auth(self.request)}
        return context
