class Video:

  def __init__(self, title, desc, link, thumbnail, duration, views, likes, comments):
    self.title = title
    self.desc = desc
    self.link = link
    self.thumbnail = thumbnail
    self.duration = duration
    self.views = views
    self.likes = likes
    self.comments = comments

  def toString(self):
    return "Title: " + self.title + "\n" + "Desc: " + self.desc + '\n' + "Link: " + self.link + '\n' + 'Thumbnail: '+ self.thumbnail + '\n' + "Duration: " + self.duration + '\nViews: ' + self.views + "\nLikes: " + self.likes + "\nComments: " + self.comments