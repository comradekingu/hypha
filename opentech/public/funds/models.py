from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models

from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.wagtailcore.fields import StreamField

from opentech.public.utils.models import BasePage

from .blocks import FundBlock


class FundPage(BasePage):
    subpage_types = []
    parent_page_types = ['FundIndex']

    introduction = models.TextField(blank=True)
    fund_type = models.ForeignKey(
        'wagtailcore.Page',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    body = StreamField(FundBlock())

    content_panels = BasePage.content_panels + [
        FieldPanel('introduction'),
        PageChooserPanel('fund_type', 'funds.FundType'),
        StreamFieldPanel('body'),
    ]


class FundIndex(BasePage):
    subpage_types = ['FundPage']
    parent_page_types = ['home.HomePage']

    def get_context(self, request, *args, **kwargs):
        funds = FundPage.objects.live().public().descendant_of(self)

        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(funds, settings.DEFAULT_PER_PAGE)
        try:
            news = paginator.page(page)
        except PageNotAnInteger:
            news = paginator.page(1)
        except EmptyPage:
            news = paginator.page(paginator.num_pages)

        context = super().get_context(request, *args, **kwargs)
        context.update(news=news)
        return context


class LabPage(BasePage):
    subpage_types = []
    parent_page_types = ['LabIndex']

    introduction = models.TextField(blank=True)
    lab_type = models.ForeignKey(
        'wagtailcore.Page',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    lab_link = models.URLField(blank=True, verbose_name="External link")
    body = StreamField(FundBlock())

    content_panels = BasePage.content_panels + [
        FieldPanel('introduction'),
        MultiFieldPanel([
            # Limit to lab pages once created
            PageChooserPanel('lab_type'),
            FieldPanel('lab_link'),
        ], heading='Link for lab application'),
        StreamFieldPanel('body'),
    ]

    def clean(self):
        if self.lab_type and self.lab_link:
            raise ValidationError({
                'lab_type': 'Cannot link to both a Lab page and external link',
                'lab_link': 'Cannot link to both a Lab page and external link',
            })

        if not self.lab_type and not self.lab_link:
            raise ValidationError({
                'lab_type': 'Please provide a way for applicants to apply',
                'lab_link': 'Please provide a way for applicants to apply',
            })


class LabIndex(BasePage):
    subpage_types = ['LabPage']
    parent_page_types = ['home.HomePage']

    introduction = models.TextField(blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel('introduction')
    ]

    def get_context(self, request, *args, **kwargs):
        funds = LabPage.objects.live().public().descendant_of(self)

        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(funds, settings.DEFAULT_PER_PAGE)
        try:
            news = paginator.page(page)
        except PageNotAnInteger:
            news = paginator.page(1)
        except EmptyPage:
            news = paginator.page(paginator.num_pages)

        context = super().get_context(request, *args, **kwargs)
        context.update(news=news)
        return context
