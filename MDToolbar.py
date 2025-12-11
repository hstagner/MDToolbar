import sublime
import sublime_plugin

BUTTONS = [
    ("B", "bold"),
    ("I", "italic"),
    ("B+I", "bold_italic"),
    ("Code", "code"),
    ("Del", "strike"),
    ("Link", "link"),
    ("Img", "image"),
    (">", "blockquote"),
]


def wrap_selection(view, edit, wrapper_type):
    """
    Apply a Markdown wrapper to all non-empty selections in the view,
    then place the caret at the end of each wrapped region with no selection.
    """
    new_carets = []

    # Work on a copy of the selection list
    for region in list(view.sel()):
        if region.empty():
            continue

        # Work with a stable region, independent of future edits
        target = sublime.Region(region.begin(), region.end())
        text = view.substr(target)

        if wrapper_type == "bold":
            new = "**{}**".format(text)
        elif wrapper_type == "italic":
            new = "_{}_".format(text)
        elif wrapper_type == "bold_italic":
            new = "**_{}_**".format(text)
        elif wrapper_type == "code":
            new = "`{}`".format(text)
        elif wrapper_type == "strike":
            new = "~~{}~~".format(text)
        elif wrapper_type == "link":
            new = "[{}](url)".format(text)
        elif wrapper_type == "image":
            new = "![{}](url)".format(text)
        elif wrapper_type == "blockquote":
            lines = view.lines(target)
            pieces = []
            for line in lines:
                line_text = view.substr(line)
                pieces.append("> " + line_text.lstrip())
            new = "\n".join(pieces)
            target = sublime.Region(lines[0].begin(), lines[-1].end())
        else:
            continue

        view.replace(edit, target, new)

        # Zero-length region = caret only, no selection
        end_pt = target.begin() + len(new)
        new_carets.append(sublime.Region(end_pt))

    if new_carets:
        sels = view.sel()
        sels.clear()
        for caret in new_carets:
            sels.add(caret)


class MdToolbarCommand(sublime_plugin.TextCommand):
    """
    Show a popup toolbar with Markdown formatting buttons for the current selection.
    """

    def run(self, edit):
        if all(r.empty() for r in self.view.sel()):
            return

        html_parts = []
        for label, action in BUTTONS:
            html_parts.append(
                '<a href="{action}" style="margin-right: 0.6em; '
                'padding: 0.1em 0.4em; border-radius: 3px; '
                'border: 1px solid var(--foreground); '
                'text-decoration: none; color: var(--foreground);">'
                "{label}</a>".format(action=action, label=label)
            )

        html = "<div>{}</div>".format("".join(html_parts))

        def on_navigate(href):
            self.view.run_command("md_toolbar_apply", {"action": href})
            self.view.hide_popup()

        self.view.show_popup(
            html,
            location=-1,
            max_width=400,
            flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY,
            on_navigate=on_navigate,
        )


class MdToolbarApplyCommand(sublime_plugin.TextCommand):
    """
    Apply the selected Markdown wrapper from the popup.
    """

    def run(self, edit, action):
        wrap_selection(self.view, edit, action)


class MdToolbarBoldCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        wrap_selection(self.view, edit, "bold")


class MdToolbarItalicCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        wrap_selection(self.view, edit, "italic")


class MdToolbarBoldItalicCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        wrap_selection(self.view, edit, "bold_italic")


class MdToolbarCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        wrap_selection(self.view, edit, "code")


class MdToolbarStrikeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        wrap_selection(self.view, edit, "strike")


class MdToolbarLinkCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        wrap_selection(self.view, edit, "link")


class MdToolbarImageCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        wrap_selection(self.view, edit, "image")


class MdToolbarBlockquoteCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        wrap_selection(self.view, edit, "blockquote")
