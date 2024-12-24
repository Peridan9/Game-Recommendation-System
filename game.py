import main_menu
import main_game

user = main_menu.main()
if user:
    main_game.main(user)
