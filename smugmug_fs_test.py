import responses
import smugmug
import smugmug_fs

import json
import unittest

API_ROOT = 'https://api.smugmug.com'

class TestSmugMugFS(unittest.TestCase):

  def setUp(self):
    self._smugmug = smugmug.FakeSmugMug()
    self._fs = self._smugmug._fs

    responses.add(responses.GET, API_ROOT + '/api/v2!authuser',
                  json=json.load(open('testdata/authuser.json')))
    responses.add(responses.GET, API_ROOT + '/api/v2/user/cmac',
                  json=json.load(open('testdata/user.json')))
    responses.add(responses.GET, API_ROOT + '/api/v2/node/zx4Fx',
                  json=json.load(open('testdata/root_node.json')))
    responses.add(responses.GET, API_ROOT + '/api/v2/node/zx4Fx!children',
                  json=json.load(open('testdata/root_children.json')))
    responses.add(responses.GET, API_ROOT + '/api/v2/node/n83bK!children',
                  json=json.load(open('testdata/folder_children.json')))

  @responses.activate
  def test_get_root_node(self):
    self.assertTrue(self._fs.get_root_node('cmac')['IsRoot'])

  @responses.activate
  def test_get_children(self):
    root_node = self._fs.get_root_node('cmac')
    root_children = self._fs.get_children(root_node)
    self.assertEquals(len(root_children), 10)
    self.assertEquals(root_children[2]['Name'], 'Photography')

    photography = root_children[2]
    photography_children = self._fs.get_children(photography)
    self.assertEquals(len(photography_children), 10)
    self.assertEquals(photography_children[0]['Name'],
                      'San Francisco by helicopter 2014')

    self.assertEquals(self._fs.get_children(photography_children[0]), [])

  @responses.activate
  def test_get_child(self):
    root_node = self._fs.get_root_node('cmac')
    photography = self._fs.get_child(root_node, 'Photography')
    self.assertEquals(photography['Name'], 'Photography')

    invalid_child = self._fs.get_child(root_node, 'Missing folder')
    self.assertIsNone(invalid_child)

  @responses.activate
  def test_path_to_node(self):
    node, matched, unmatched = self._fs.path_to_node('cmac', '')
    self.assertTrue(node['IsRoot'])
    self.assertEquals(matched, [])
    self.assertEquals(unmatched, [])

    node, matched, ummatched = self._fs.path_to_node('cmac', '/')
    self.assertTrue(node['IsRoot'])
    self.assertEquals(matched, [])
    self.assertEquals(unmatched, [])

    node, matched, ummatched = self._fs.path_to_node('cmac', 'Photography')
    self.assertEquals(node['Name'],'Photography')
    self.assertEquals(matched, ['Photography'])
    self.assertEquals(unmatched, [])

    node, matched, ummatched = self._fs.path_to_node('cmac', '/Photography')
    self.assertEquals(node['Name'], 'Photography')
    self.assertEquals(matched, ['Photography'])
    self.assertEquals(unmatched, [])

    node, matched, unmatched = self._fs.path_to_node(
        'cmac', '/Photography/San Francisco by helicopter 2014')
    self.assertEquals(node['Name'], 'San Francisco by helicopter 2014')
    self.assertEquals(matched, ['Photography',
                                'San Francisco by helicopter 2014'])
    self.assertEquals(unmatched, [])

    node, matched, unmatched = self._fs.path_to_node('cmac', '/invalid1')
    self.assertTrue(node['IsRoot'])
    self.assertEquals(matched, [])
    self.assertEquals(unmatched, ['invalid1'])

    node, matched, unmatched = self._fs.path_to_node(
      'cmac', '/Photography/invalid2')
    self.assertEquals(node['Name'], 'Photography')
    self.assertEquals(matched, ['Photography'])
    self.assertEquals(unmatched, ['invalid2'])

if __name__ == '__main__':
  unittest.main()
