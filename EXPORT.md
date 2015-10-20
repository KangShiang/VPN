### Export README to PDF

In chrome, add a bookmark to export to a PDF saveable page:

1. In Chrome, click Bookmarks -> Bookmark Manager.
1. You should see a new tab with the bookmarks and folders listed.
1. Select the "Bookmarks Tab" folder on the left.
1. Click the "Organize" link, then "Add Page" in the drop down.
1. You should see two input fields. ...
1. Set the first, name field to `GitHub.md to PDF`
1. Paste the javascript code below into the second field.

  ```
javascript:(function(e,a,g,h,f,c,b,d)%7Bif(!(f=e.jQuery)%7C%7Cg%3Ef.fn.jquery%7C%7Ch(f))%7Bc=a.createElement(%22script%22);c.type=%22text/javascript%22;c.src=%22http://ajax.googleapis.com/ajax/libs/jquery/%22+g+%22/jquery.min.js%22;c.onload=c.onreadystatechange=function()%7Bif(!b&&(!(d=this.readyState)%7C%7Cd==%22loaded%22%7C%7Cd==%22complete%22))%7Bh((f=e.jQuery).noConflict(1),b=1);f(c).remove()%7D%7D;a.documentElement.childNodes%5B0%5D.appendChild(c)%7D%7D)(window,document,%221.3.2%22,function($,L)%7B$('%23header,%20.pagehead,%20.breadcrumb,%20.commit,%20.meta,%20%23footer,%20%23footer-push,%20.wiki-actions,%20%23last-edit,%20.actions,%20.header,.site-footer,.repository-sidebar,.file-navigation,.file-header,.gh-header-meta,.gh-header-actions,#wiki-rightbar,#wiki-footer').remove();%20$('%23files,%20.file').css(%7B%22background%22:%22none%22,%20%22border%22:%22none%22%7D);%20$('link').removeAttr('media');%7D);
  ```

1. Run the bookmarklet on the `README.md` rendering from GitHub
1. Print -> Save as PDF
1. Add PDF to REPO if necessary
