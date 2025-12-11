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
    then place the caret at the end of each wrapped region (no selection).
    """
    new_carets = []

    for region in list(view.sel()):
        if region.empty():
            continue

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

        end_pt = target.begin() + len(new)
        new_carets.append(sublime.Region(end_pt))

    if new_carets:
        sels = view.sel()
        sels.clear()
        for caret in new_carets:
            sels.add(caret)


def _clear_to_single_caret(view):
    """
    Final cleanup: ensure only a single caret exists, no selection.
    """
    sels = view.sel()
    if len(sels) == 0:
        return
    last_pt = sels[-1].end()
    sels.clear()
    sels.add(sublime.Region(last_pt))


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
        _clear_to_single_caret(self.view)


class MdToolbarBoldCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        wrap_selection(self.view, edit, "bold")
        _clear_to_single_caret(self.view)


class MdToolbarItalicCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        wrap_selection(self.view, edit, "italic")
        _clear_to_single_caret(self.view)


class MdToolbarBoldItalicCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        wrap_selection(self.view, edit, "bold_italic")
        _clear_to_single_caret(self.view)


class MdToolbarCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        wrap_selection(self.view, edit, "code")
        _clear_to_single_caret(self.view)


class MdToolbarStrikeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        wrap_selection(self.view, edit, "strike")
        _clear_to_single_caret(self.view)


class MdToolbarLinkCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        wrap_selection(self.view, edit, "link")
        _clear_to_single_caret(self.view)


class MdToolbarImageCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        wrap_selection(self.view, edit, "image")
        _clear_to_single_caret(self.view)


class MdToolbarBlockquoteCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        wrap_selection(self.view, edit, "blockquote")
        _clear_to_single_caret(self.view)
