import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    '''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Contorl-Allow-Headers',
                             'Content-Type, Athurization true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        listCategory = {}
        for category in categories:
            listCategory[category.id] = category.type
        return jsonify({
          'success': True,
          'categories': listCategory,
        })

    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom
    of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * 10
            end = start + 10
            questions = Question.query.order_by(Question.id).all()
            formatted_question = [question.format() for question in questions]
            paginate_questions = formatted_question[start:end]
            numOfCategories = len(Category.query.all())

            if (len(paginate_questions) == 0):
                abort(404)

            return jsonify({
                'success': True,
                'questions': paginate_questions,
                'numOfQuestions': len(questions),
                'current_category': 'None',
                'categories': numOfCategories
            })
        except Exception as e:
            abort(404)
    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question,
    the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if(question is None):
                abort(422)
            question.delete()
            numOfquestions = len(Question.query.all())
            return jsonify({
                'success': True,
                'question_id': question_id,
                'numOfQuestions': numOfquestions})
        except Exception as e:
            abort(422)

    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear
    at the end of the last page
    of the questions list in the "List" tab.
    '''
    @app.route('/questions', methods=['POST'])
    def add_question():
        try:
            body = request.get_json()
            question = Question(question=body.get('question', None),
                                answer=body.get('answer', None),
                                difficulty=body.get('difficulty', 0),
                                category=body.get('category', None))
            question.insert()
            return jsonify({
                'success': True,
                'question': question.format(),
                'numOfQuestions': len(Question.query.all())
            })
        except Exception as e:
            abort(405)

    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    @app.route('/questions/search', methods=['POST'])
    def search_question():
        body = request.get_json()
        search = body.get('searchTerm', None)
        if(search is None):
            abort(404)

        result = Question.query.filter(Question.question.ilike
                                       (f'%{search}%')).all()
        if (result is None):
            abort(404)

        return jsonify({
            'success': True,
            'questions': [question.format() for question in result],
            'total_questions': len(result)
        })

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def questions_by_category(category_id):
        try:
            questions = Question.query.filter(Question.category ==
                                              str(category_id)).all()
            if(questions is None):
                abort(404)
            return jsonify({
                 'success': True,
                 'category': category_id,
                 'questions': [question.format() for question in questions],
                 'numOfQuestions': len(questions)
            })
        except Exception as e:
            abort(404)

    '''
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    @app.route('/quizzes', methods=['POST'])
    def quiz():
        try:
            body = request.get_json()
            if ('previous_questions' is None or 'quiz_category' is None):
                abort(404)

            preQuestion = body.get('previous_questions')
            category = body.get('quiz_category')

            if(category['id'] == 0):
                questions = Question.query.all()

            else:
                questions = Question.query.filter(Question.category ==
                                                  category['id']).all()

            def get_random_question():
                return questions[random.randrange(0, len(questions), 1)]

            nextQuestion = get_random_question()
            isPre = True
            while isPre:
                if nextQuestion.id in preQuestion:
                    nextQuestion = get_random_question()

                else:
                    isPre = False

            return jsonify({
                 'success': True,
                 'question': nextQuestion.format()
            })
        except Exception as e:
            abort(422)
    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
           }), 422

    @app.errorhandler(405)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method Not Allowed"
           })

    return app
