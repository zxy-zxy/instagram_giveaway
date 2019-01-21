# Instagram giveaway
### This script may help you to filter users to participate in your instagram post contest.

## Requirements
Python >= 3.5 required.  
Install dependencies with 
```bash
pip install -r requirements.txt
```
For better interaction is recommended to use [virtualenv](https://github.com/pypa/virtualenv).

## Usage

Create .env file and store your account name and password in ***instagram_login*** and 
***instagram_password*** variables. 

Script will prepare a list of valid users to take participation in your giveaway.
Script filters commentators of the post by the following conditions:
* Commentator tagged** his friends in comment and friends are exists.
* Mentioned friend is his follower.
* Commentator liked the post.
* Commentator has followed the author.

Run script with parameter:
```bash
python instagram_giveaway.py https://www.instagram.com/p/BrbkCltHo2K
```