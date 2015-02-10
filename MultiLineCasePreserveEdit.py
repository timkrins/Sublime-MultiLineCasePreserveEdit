'''
_|_. _ _ |  _. _  _
 | || | ||<| || |_\

sublime text case-preserved multiple editing
author: tim krins
contact: me@timkrins.com
version: 0.1a

issues:
- undo is not working correctly
- probably destroys all other plugins in its wake
- needs tests and extensive testing
- it will delete your entire file if you sneeze

I accept no responsibility for this plugin destroying your computer etc

'''

import sublime, sublime_plugin, random, string

'''
example:

Spaghetti
spaghetti
spagHetti
SPAGHETTI

we can change all the spaghettis to

Ravioli
ravioli
Ravioli
RAVIOLI

by using the shift-key on the first letter only (note: the third case speciality in this example will be lost)

Plugin is activated when differing cases are detected.

'''

class MultiLineCasePreserveEditCommand(sublime_plugin.TextCommand):  
    def run(self, edit, func_input=None):  
        # Walk through each region in the selection
        if func_input:
            for item in func_input:
                # get region
                region = sublime.Region(item[0][0], item[0][1])
                # get string
                text = self.view.substr(region)
                if item[1] == "lower":
                    text_replace = text.lower()
                    self.view.replace(edit, region, text_replace)
                elif item[1] == "upper":
                    text_replace = text.upper()
                    self.view.replace(edit, region, text_replace)
                elif item[1] == "mixed":
                    None

class MultiLineCasePreservation(sublime_plugin.EventListener):
    def __init__(self):
        self.tracked_selections = []
        self.last_selections = []
        print("MultiLineCasePreservationPlugin loaded")

    def process_selections(self, view, selections):
        if(len(selections) > 1):
            self.tracked_selections = selections

    def on_modified_async(self, view):
        current_startings = []
        current_endings = []
        # get beginning cursor initial_startings
        for v in view.sel():
            current_startings.append(v.a)
            current_endings.append(v.b)
        # now lets get all the cursors, and if we have the same amount of cursors, say hi!
        # if we have not changed since last time, return
        if set(current_startings + current_endings) != set(self.last_selections):
            self.last_selections = current_startings + current_endings
            cursors_len = len(view.sel())
            if (cursors_len == len(self.tracked_selections)):
                # cycle through beginnings and ending regions and convert their case according to tracked selections
                initial_startings = []
                initial_endings = []
                regions = []
                transforms = []
                addings = []

                # get beginning cursor initial_startings
                for s in self.tracked_selections:
                    initial_startings.append(min(s['pos']))
                    initial_endings.append(max(s['pos']))
                    transforms.append(s['mod'])

                # here is the modifiers
                for i in range(len(initial_endings)):
                    addings.append(current_startings[0] - initial_startings[0])

                modifier = 0
                for i in range(len(initial_startings)):
                    original_dist = abs(initial_endings[i] - initial_startings[i]) # original length of this content
                    current_dist = addings[i] # length of this string from beginning
                    difference = current_dist - original_dist # difference between the string lengths
                    modifier = difference * (i)
                    regions.append([[initial_startings[i] + modifier, current_endings[i]], transforms[i], difference])

                # place modifications into the editor via TextCommand (have no other way in ST3)
                # only run this if we have multiple cases
                transform_set = set(transforms)
                if len(transform_set) > 1:
                    view.run_command('multi_line_case_preserve_edit', {"func_input": regions} )

    def on_selection_modified_async(self, view):
        if len(view.sel()) > 1:
                current_selections = []
                for s in view.sel():
                    r = {}
                    r['pos'] = (s.a, s.b)
                    region = s
                    text = view.substr(region)
                    if(text):
                        if text.islower():
                            r['mod'] = 'lower'
                        elif text.isupper():
                            r['mod'] = 'upper'
                        else:
                            r['mod'] = 'mixed'
                        current_selections.append(r)

                # now, we have all our selections.
                self.process_selections(view, current_selections)
        else:
            if(len(self.tracked_selections) > 1):
                self.tracked_selections = []