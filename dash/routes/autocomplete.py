from sanic import Blueprint
from sanic import response

from fast_autocomplete import AutoComplete
import json


autocomplete = Blueprint('autocomplete', url_prefix='/autocomplete')


models_directory = './autocomplete'
autocomplete_models = {
    'en': AutoComplete(words=json.load(open(f'{models_directory}/en.json', 'r'))),
    'es': AutoComplete(words=json.load(open(f'{models_directory}/es.json', 'r'))),
    'fr': AutoComplete(words=json.load(open(f'{models_directory}/fr.json', 'r'))),
    'pt': AutoComplete(words=json.load(open(f'{models_directory}/pt.json', 'r')))
}


@autocomplete.post('/')
async def complete(request):
    lang = request.args.get('language', 'en')
    query = request.args.get('text')
    limit = request.args.get('limit', 7)
    model = autocomplete_models.get(lang, autocomplete_models['en'])

    if any(stop in query for stop in ['.', '?', '!']):
        return response.json([])
    elif query.count(' ') >= int(limit):
        return response.json([])

    potential_words = []
    tokens = query.lower().rsplit(' ', 3)

    for i in range(min(3, len(tokens)), 0, -1):
        results = model.search(' '.join(tokens[-i:]), max_cost=10, size=10)
        words = [token for phrases in results for token in phrases[-1].split() if token.startswith(tokens[-1])]
        potential_words += words

    result = [{
        'text': word.capitalize() if len(tokens) == 1 else query.rsplit(' ', 1)[0] + ' ' + word,
        'is_match': True,
        'can_send': True
    } for word in dict.fromkeys(potential_words)]

    return response.json(result[:12])
