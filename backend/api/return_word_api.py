from flask import Blueprint, jsonify

wordbp=Blueprint('word', __name__)
@wordbp.route('/word', methods=['POST'])
def word():
    '''
    返回每个年纪对应单元以及每一课的word
    Returns
    -------
    '''
