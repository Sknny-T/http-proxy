from pywebcopy import save_website


print("Please type in the Website you want to copy!")

website = input()

save_website(url=website, project_folder="//home/osboxes/Documents/Websites/")
