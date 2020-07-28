from app import app
import views.view_home
import views.view_install
import views.view_authorize
import views.view_finalize
import views.view_create_order
import views.view_ecocart
import views.view_activatecharge
import views.view_settings
import views.view_ecocart_json
import views.view_ecocart_js
import views.view_style
import views.view_index
import views.view_reset
import views.view_instruction
import views.view_uninstalled


if __name__ == '__main__':
    app.run(app.config.get('IP'), app.config.get('PORT'), app.config.get('DEBUG'))
