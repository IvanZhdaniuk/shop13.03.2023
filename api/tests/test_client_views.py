# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from ..models import Category
from ..views import CategoriesListView
from django.urls import reverse


class TestCategoriesView(TestCase):
    fixtures = ["api/tests/fixtures/fixture_categories.json"]


    def test_categories_all_view(self):
        response = self.client.get(reverse('categories-all'))
        self.assertIsInstance(response.data, list)
        self.assertEqual(response.data, [
            {
                "id": 1,
                "name": "category1",
                "description": "some description"
            },
            {
                "id": 2,
                "name": "category2",
                "description": "some description"
            },
            {
                "id": 3,
                "name": "category3",
                "description": "some description"
            }

        ])






