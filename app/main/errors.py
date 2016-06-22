from flask import render_template, redirect, url_for
from . import main

# Error Handling
@main.errorhandler(401)
def logged_out(e):
    flash("You are currently logged out. Please log in.")
    return redirect(url_for('index'))

@main.errorhandler(404)
def page_not_found(e):
  return render_template('404.html'), 404

@main.errorhandler(500)
def internal_server_error(e):
  return render_template('500.html'), 500