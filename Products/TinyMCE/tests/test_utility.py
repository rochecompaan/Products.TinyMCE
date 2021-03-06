import os

import transaction
from Products.CMFCore.utils import getToolByName
from plone.testing.z2 import Browser

from Products.TinyMCE.tests.base import IntegrationTestCase
from Products.TinyMCE.utility import form_adapter


class UtilityTestCase(IntegrationTestCase):

    def setUp(self):
        super(UtilityTestCase, self).setUp()
        self.utility = form_adapter(self.portal)

    def test_tinymce_configuration(self):
        # Let's get the configuration of TinyMCE and see if it returns a json structure.
        self.assertTrue(self.utility.getConfiguration(self.portal))

        # Now let's change some variables and see it still works.
        self.utility.toolbar_cut = True
        self.utility.toolbar_copy = True
        self.utility.toolbar_paste = True
        self.utility.toolbar_pastetext = True
        self.utility.toolbar_pasteword = True
        self.utility.toolbar_undo = True
        self.utility.toolbar_redo = True
        self.utility.toolbar_search = True
        self.utility.toolbar_replace = True
        self.utility.toolbar_underline = True
        self.utility.toolbar_strikethrough = True
        self.utility.toolbar_sub = True
        self.utility.toolbar_sup = True
        self.utility.toolbar_forecolor = True
        self.utility.toolbar_backcolor = True
        self.utility.toolbar_media = True
        self.utility.toolbar_charmap = True
        self.utility.toolbar_hr = True
        self.utility.toolbar_advhr = True
        self.utility.toolbar_insertdate = True
        self.utility.toolbar_inserttime = True
        self.utility.toolbar_emotions = True
        self.utility.toolbar_nonbreaking = True
        self.utility.toolbar_pagebreak = True
        self.utility.toolbar_print = True
        self.utility.toolbar_preview = True
        self.utility.toolbar_spellchecker = True
        self.utility.toolbar_removeformat = True
        self.utility.toolbar_cleanup = True
        self.utility.toolbar_visualaid = True
        self.utility.toolbar_visualchars = True
        self.utility.toolbar_attribs = True
        self.utility.resizing = False

        # The result should at least contain the new buttons we added.
        self.assertRegexpMatches(self.utility.getConfiguration(self.portal), '\{.+attribs.+}')

        # Let's change some more settings.
        self.utility.toolbar_external = True
        self.utility.autoresize = True
        self.utility.editor_width = u'100'
        self.utility.editor_height = u'abc'
        self.utility.toolbar_width = u'abc'
        self.utility.contextmenu = False
        self.utility.content_css = u'test.css'
        self.utility.link_using_uids = True
        self.utility.allow_captioned_images = True
        self.utility.rooted = True

        props = getToolByName(self, 'portal_properties')
        livesearch = props.site_properties.getProperty('enable_livesearch', False)
        livesearch = False
        livesearch  # pep8

        # The result should contain the settings specified.
        self.assertRegexpMatches(self.utility.getConfiguration(self.portal), '\{.+external.+}')

        # Let's call the portal_factory of a document and make sure the configuration
        # doesn't contain the save button:
        browser = Browser(self.app)
        self.app.acl_users.userFolderAddUser('root', 'secret', ['Manager'], [])
        transaction.commit()
        browser.addHeader('Authorization', 'Basic root:secret')
        browser.open('http://nohost/plone/createObject?type_name=Document')
        self.assertNotIn("&quot;save&quot;:", browser.contents)

        # Do some more toolbar tests, specifically testing the spellchecker button.
        # First, we make sure that no spellchecker is loaded when the toolbar button is
        # hidden.
        self.utility.toolbar_spellchecker = False
        transaction.commit()
        browser.open('http://nohost/plone/createObject?type_name=Document')

        # AtD shouldn't be there:
        self.assertNotIn("&quot;AtD&quot;", browser.contents)

        # Neither should iespell:
        self.assertNotIn("&quot;iespell&quot;", browser.contents)

        # Now, we enable the button and set AtD as the checker:
        self.utility.toolbar_spellchecker = True
        self.utility.libraries_spellchecker_choice = u'AtD'
        transaction.commit()
        browser.open('http://nohost/plone/createObject?type_name=Document')
        self.assertIn("&quot;AtD&quot;", browser.contents)

        # Now, we set iespell as the checker:
        self.utility.libraries_spellchecker_choice = u'iespell'
        transaction.commit()
        browser.open('http://nohost/plone/createObject?type_name=Document')
        self.assertIn("&quot;iespell&quot;", browser.contents)

        # When we have browser as the checker, neither iespell nor AtD should load:
        self.utility.libraries_spellchecker_choice = u'browser'
        transaction.commit()
        browser.open('http://nohost/plone/createObject?type_name=Document')
        self.assertNotIn("&quot;iespell&quot;", browser.contents)
        self.assertNotIn("&quot;AtD&quot;", browser.contents)

    def test_tinymce_configurable_image_dimensions(self):
        # The image scale dimensions being provided to the image chooser should be
        # gathered from the chosen AT content type. Let's begin by creating an
        # AT image:
        id = self.portal.invokeFactory('News Item', id='test')
        self.assertEqual(repr(self.portal[id]), '<ATNewsItem at /plone/test>')

        # Now the values being provided through JSON should be gotten from the ATNewsItem
        # schema:
        primary_field = self.portal.test.schema['image']
        scales = self.utility.getImageScales(primary_field)
        self.assertEqual(scales,
            [{'size': [0, 0], 'title': 'Original', 'value': ''},
            {'size': [16, 16], 'title': 'Listing', 'value': 'image_listing'},
            {'size': [32, 32], 'title': 'Icon', 'value': 'image_icon'},
            {'size': [64, 64], 'title': 'Tile', 'value': 'image_tile'},
            {'size': [128, 128], 'title': 'Thumb', 'value': 'image_thumb'},
            {'size': [200, 200], 'title': 'Mini', 'value': 'image_mini'},
            {'size': [400, 400], 'title': 'Preview', 'value': 'image_preview'},
            {'size': [768, 768], 'title': 'Large', 'value': 'image_large'}]
        )

        # If no primary field is given, we should get the scale dimensions from ATImage:
        scales = self.utility.getImageScales()
        self.assertEqual(scales,
            [{'size': [0, 0], 'title': 'Original', 'value': ''},
            {'size': [16, 16], 'title': 'Listing', 'value': 'image_listing'},
            {'size': [32, 32], 'title': 'Icon', 'value': 'image_icon'},
            {'size': [64, 64], 'title': 'Tile', 'value': 'image_tile'},
            {'size': [128, 128], 'title': 'Thumb', 'value': 'image_thumb'},
            {'size': [200, 200], 'title': 'Mini', 'value': 'image_mini'},
            {'size': [400, 400], 'title': 'Preview', 'value': 'image_preview'},
            {'size': [768, 768], 'title': 'Large', 'value': 'image_large'}]
        )

        # We need to specify a context, if we want the dimension of the original image
        imgdata = open(os.path.join(os.path.dirname(__file__), 'sample.png'))
        self.portal[id].setImage(imgdata)

        scales = self.utility.getImageScales(context=self.portal[id])
        self.assertEqual(scales,
            [{'size': [52, 43], 'title': 'Original', 'value': ''},
            {'size': [16, 16], 'title': 'Listing', 'value': 'image_listing'},
            {'size': [32, 32], 'title': 'Icon', 'value': 'image_icon'},
            {'size': [64, 64], 'title': 'Tile', 'value': 'image_tile'},
            {'size': [128, 128], 'title': 'Thumb', 'value': 'image_thumb'},
            {'size': [200, 200], 'title': 'Mini', 'value': 'image_mini'},
            {'size': [400, 400], 'title': 'Preview', 'value': 'image_preview'},
            {'size': [768, 768], 'title': 'Large', 'value': 'image_large'}]
        )
