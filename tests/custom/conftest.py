import pytest

TEMPLATE = """
<%firstName%> <%lastName%> <%>id%> is an <%occupation%>
<%= {{ }} =%>
Affirmatives:
{{#affirmatives}}
  {{>affirmative}}

{{/affirmatives}}
 0. {{affirmatives.0.status}}
 3. {{affirmatives.3.status}}
-1. {{affirmatives.-1.status}}
-2. {{affirmatives.-2.status}}
{{! is this a comment? }}
Condition: {{>cond}}
"""
DATA = """
{
  "id": 70,
  "firstName": "Sliver",
  "lastName": "of Straw",
  "occupation": "Iterator",
  "affirmatives": [
    {"name": "First", "status": true},
    {"name": "Second", "status": true},
    {"name": "Third", "status": true},
    {"name": "Always False", "status": false}
  ],
  "condition": "Dead"
}
"""

PARTIAL_1 = '{{name}}: {{#status}}✓{{/status}}{{^status}}✗{{/status}}'
PARTIAL_2 = '(id{{id}})'
PARTIAL_3 = '> {{condition}} <'

EXPECTED = """
Sliver of Straw (id70) is an Iterator
Affirmatives:
  First: ✓
  Second: ✓
  Third: ✓
  Always False: ✗
 0. True
 3. False
-1. False
-2. True
Condition: > Dead <
"""


@pytest.fixture(scope='session')
def clidir(tmp_path_factory: pytest.TempPathFactory):
    tmp_path = tmp_path_factory.mktemp('clidir')
    (tmp_path / 'partials').mkdir()

    (tmp_path / 'template.txt').write_text(TEMPLATE)
    (tmp_path / 'data.json').write_text(DATA)
    (tmp_path / 'partials/affirmative.mustache').write_text(PARTIAL_1)
    (tmp_path / 'partials/id.mustache').write_text(PARTIAL_2)
    (tmp_path / 'cond.mustache').write_text(PARTIAL_3)
    return tmp_path
