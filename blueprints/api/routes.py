from flask import jsonify
from . import api_bp
from models import Trek

@api_bp.route('/treks')
def get_treks():
    treks = Trek.query.all()
    return jsonify([{
        'id': t.id,
        'name': t.name,
    } for t in treks])