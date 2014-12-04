import json
import urllib2

import mock
import unittest2

from appfy.recipe.gae import sdk


class BaseTestCase(unittest2.TestCase):

    @classmethod
    def get_buildout(cls, custom_config=None):
        """Returns a fake instance of zc.buildout.buildout.Buildout

        """
        config = {
            'buildout': {
                # 'socket-timeout': '',
                # 'newest': 'true',
                # 'installed': '/project-dir/.installed.cfg',
                # 'executable': '/usr/local/opt/python/bin/python2.7',
                # 'develop': '.',
                # 'parts': 'app_lib\ngae_sdk\ngae_tools\ntest',
                # 'offline': 'false',
                'parts-directory': '/non-existing-dir/parts',
                # 'bin-directory': '/project-dir/bin',
                # 'install-from-cache': 'false',
                # 'eggs-directory': '/project-dir/eggs',
                # 'python': 'buildout',
                # 'use-dependency-links': 'true',
                # 'eggs': 'gae_buildout_example\npdbpp',
                # 'allow-picked-versions': 'true',
                # 'find-links': '',
                # 'log-format': '',
                # 'show-picked-versions': 'false',
                # 'update-versions-file': '',
                # 'prefer-final': 'true',
                # 'allow-hosts': '*',
                # 'versions': 'versions',
                # 'develop-eggs-directory': '/project-dir/develop-eggs',
                # 'log-level': 'INFO',
                'directory': '/non-existing-dir',
            },
            # 'versions': {
            #     'zc.buildout': '>=2.2.5',
            #     'zc.recipe.egg': '>=2.0.0a3'
            # },
            # 'gae_tools': {
            #     'extra-paths': 'src/lib\nsrc/lib',
            #     'sdk-directory': '/project-dir/parts/google_appengine',
            #     'recipe': 'appfy.recipe.gae:tools'
            # },
            # 'gae_sdk': {
            #     'url': 'https://www.gion=1414431206531000&alt=media',
            #     'clear-destination':'true',
            #     'destination': '/gae_buildout_example/parts',
            #     'recipe': 'appfy.recipe.gae:sdk',
            #     'hash-name': 'false'
            # },
            # 'app_lib': {
            #     'bin-directory': '/gae_buildout_example/bin',
            #     'unzip': 'true',
            #     'ignore-globs': 'ests\n*/testsuite\n*/django\n*/sqlalchemy',
            #     'eggs-directory': '/gae_buildout_example/eggs',
            #     'eggs': 'gae_buildout_example\npdbpp',
            #     'recipe': 'appfy.recipe.gae:app_lib',
            #     'develop-eggs-directory': '/project-dir/develop-eggs',
            #     'lib-directory': 'src/lib',
            #     'use-zipimport': 'false',
            #     '_e': 'gae_buildout_example/eggs',
            #     '_d': 'gae_buildout_example/develop-eggs',
            #     '_b': 'gae_buildout_example/bin',
            #     'ignore-packages': 'webtest\nwaitress'
            # }
        }

        if custom_config:
            config.update(custom_config)

        return config


class TestSdkRecipe(BaseTestCase):

    part_name = 'gae_sdk'

    @mock.patch.object(sdk.Recipe, 'find_latest_sdk_url')
    def test_default_options(self, mock_find_sdk):
        buildout = self.get_buildout()
        options = {}

        recipe = sdk.Recipe(buildout, self.part_name, options)

        expected_options = {
            'url': mock_find_sdk.return_value,
            'destination': buildout['buildout']['parts-directory'],
            'clear-destination': 'true',
            'download-only': 'false',
            'hash-name': 'false',
            'strip-top-level-dir': 'false'
        }
        self.assertEqual(
            recipe.options,
            expected_options
        )
        self.assertTrue(mock_find_sdk.called)

    @mock.patch.object(sdk.Recipe, 'find_latest_sdk_url')
    def test_do_search_for_sdk_when_url_provided(self, mock_find_sdk):
        buildout = self.get_buildout()
        sdk_url = 'http://this.is.some.url'
        options = {'url': sdk_url}

        recipe = sdk.Recipe(buildout, self.part_name, options)

        self.assertEqual(recipe.options['url'], sdk_url)
        self.assertFalse(mock_find_sdk.called)

    @mock.patch.object(sdk.Recipe, 'find_latest_sdk_url')
    def test_options_are_possible_to_set(self, mock_find_sdk):
        buildout = self.get_buildout()
        options = {
            'destination': '/where/to/download/',
            'url': 'some-url',
            'clear-destination': 'some-value',
            'download-only': 'some-value',
            'hash-name': 'some-value',
            'strip-top-lever-dir': 'some-value',
        }

        recipe = sdk.Recipe(buildout, self.part_name, options)
        recipe.get_ordered_sdks_urls()
        self.assertEqual(
            recipe.options,
            options
        )

    @mock.patch.object(sdk.Recipe, 'is_sdk_avaiable')
    @mock.patch.object(sdk.Recipe, 'get_ordered_sdks_urls')
    def test_get_latest_available_sdk(self, mock_get_sdks,
                                      mock_is_avaiable):
        mock_get_sdks.return_value = (
            u'featured/google_appengine_2.0.0.zip',
            u'featured/google_appengine_0.0.15.zip'
        )
        mock_is_avaiable.side_effect = (
            False,
            True,
        )
        self.assertEqual(
            sdk.Recipe.find_latest_sdk_url(),
            'featured/google_appengine_0.0.15.zip'
        )

    @mock.patch('appfy.recipe.gae.sdk.urllib2.urlopen')
    def test_get_sdks_urls_from_google_bucket(self, mock_urlopen):
        bucket = json.dumps({
            'items': [
                {u'name': u'featured/go_google_appengine_2.0.0.zip',
                 u'mediaLink': u'featured/go_google_appengine_2.0.0.zip'},
                {u'name': u'featured/google_appengine_0.0.15.zip',
                 u'mediaLink': u'featured/google_appengine_0.0.15.zip'},
                {u'name': u'featured/google_appengine_2.0.0.zip',
                 u'mediaLink': u'featured/google_appengine_2.0.0.zip'},
                {u'name': u'featured/google_appengine_2.0.0.msi',
                 u'mediaLink': u'featured/google_appengine_2.0.0.msi'},
            ]
        })
        mock_urlopen.return_value.read.return_value = bucket
        sdks = sdk.Recipe.get_ordered_sdks_urls()
        expected_sdks = [
            u'featured/google_appengine_2.0.0.zip',
            u'featured/google_appengine_0.0.15.zip',
        ]
        self.assertEqual(sdks, expected_sdks)

    @mock.patch.object(sdk.Recipe, 'get_ordered_sdks_urls')
    def test_raise_error_when_no_sdk_avaiable(self, mock_get_sdks):
        mock_get_sdks.return_value = ()
        with self.assertRaises(sdk.SDKCouldNotBeFound):
            sdk.Recipe.find_latest_sdk_url(),

    def test_get_only_sdk_with_highest_version(self):
        sdks = (
            {u'name': u'featured/google_appengine_0.0.15.zip',
                u'mediaLink': u'featured/google_appengine_0.0.15.zip'},
            {u'name': u'featured/google_appengine_2.0.0.zip',
                u'mediaLink': u'featured/google_appengine_2.0.0.zip'},
            {u'name': u'featured/google_appengine_1.9.15.zip',
                u'mediaLink': u'featured/google_appengine_1.9.15.zip'},
            {u'name': u'featured/google_appengine_1.9.1.zip',
                u'mediaLink': u'featured/google_appengine_1.9.1.zip'},
            {u'name': u'featured/google_appengine_1.9.14.zip',
                u'mediaLink': u'featured/google_appengine_1.9.14.zip'},
        )
        sorted_sdks = sdk.Recipe._sort_sdk_by_version(sdks)

        self.assertIn('2.0.0', sorted_sdks[0]['name'])
        self.assertIn('0.0.15', sorted_sdks[-1]['name'])

    @mock.patch('appfy.recipe.gae.sdk.urllib2')
    def test_sdk_is_avaiable(self, mock_urllib):
        url = 'some-url'
        result = sdk.Recipe.is_sdk_avaiable(url)
        request = mock_urllib.urlopen.call_args[0][0]

        self.assertEqual(request.get_method(), 'HEAD')
        self.assertEqual(request.get_full_url(), url)
        self.assertTrue(result)

    @mock.patch('appfy.recipe.gae.sdk.urllib2.urlopen')
    def test_sdk_is_not_avaiable_when_restricted(self, mock_urlopen):
        for error_code in (401, 403):

            error = urllib2.HTTPError(*[None] * 5)
            error.code = error_code
            mock_urlopen.side_effect = error

            self.assertFalse(
                sdk.Recipe.is_sdk_avaiable('some-url')
            )

    @mock.patch('appfy.recipe.gae.sdk.urllib2.urlopen')
    def test_unknown_error_when_check_for_sdk(self, mock_urlopen):
        for error_code in (400, 405, 500, 503):
            error = urllib2.HTTPError(*[None] * 5)
            error.code = error_code
            mock_urlopen.side_effect = error

            with self.assertRaises(urllib2.HTTPError):
                sdk.Recipe.is_sdk_avaiable('some-url')
