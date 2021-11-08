# defines classes used in markov_modeling.ipynb, moved here for improved readability

import re
import os
import markovify
import spacy
nlp = spacy.load("en_core_web_sm")

# markov_modeling-specific class definitions
# this defines the class that we will make an instance of to do our file and model management;
# i recommend reading a function's description if you want to know what it is/how to use it
class markovManager(dict):
    def __init__(self, root_folder):
        '''
        Initializes an instance of markovManager given the root folder where data is stored, defined in File Manager.
        Note that this runs directory_setup(), which means it will check for folders called "txts/" and "jsons/".
        If these folders do not exist, it will create them. 
        These are where your .txt and markovify .jsons should be stored, and where jsons will be written out.
        '''
        self.root_folder = root_folder
        # if you want to change where text files are read from, this is where you'll do it
        self.txts_folder = self.root_folder+"txts/"
        # if you want to change where json files are read from and saved to, this is where you'll do it
        self.jsons_folder = self.root_folder+"jsons/"
        self.folders = [self.root_folder, self.txts_folder, self.jsons_folder]
        self.directory_setup(self.folders)
        
        # creates dictionary that maps filenames in txts folder (w/o extension) to contents from the associated files
        self.txts = self.folder_to_dict(self.txts_folder)
        # creates dictionary that maps filenames in jsons folder (w/o extension) to contents from the associated files
        self.jsons = self.folder_to_dict(self.jsons_folder)
        # creates dictionary that maps filenames in the jsons folder (w/o extension) to markovify model objects
        self.models = {key:self.json_interpreter(self.jsons[key]) for key in self.jsons.keys()}
        self.data = [self.txts, self.jsons, self.models]

# NOTE: the next set of functions are ones you generally will *not* be calling
    def directory_setup(self, folders):
        '''
        Checks the root_folder for subfolders called "txts" and "jsons"; if they do not exist, they will be created.
        Note this runs upon initialization, but should not generally be called.
        '''
        for folder in folders:
            if os.path.isdir(folder) == False:
                path_out = (os.getcwd()+"/"+folder).replace("\\", "/")
                print("creating {}".format(path_out))
                os.mkdir(folder)
    
    def file_reader(self, path):
        '''
        Receives a string representing a filepath, and returns a string of that file's contents.
        Note that you will generally not be running this function; it's used for other functions you will use.
        '''
        with open(path, 'r', errors="ignore") as f:
            content = f.read()
        return content
    
    def json_interpreter(self, json):
        '''
        Receives a string of json representing a stored markovify model, and returns a markovify model object.
        Note that it checks if the model represented by the json is POSified or just a regular markovify object.
        Note that you will generally not be running this function; it's used for other functions you will use.
        '''
        if "::" in json:
            model = POSifiedText.from_json(json)
        else:
            model = markovify.Text.from_json(json)
        return model
    
    def folder_to_dict(self, folder):
        '''
        Receives a string representing a folder path, and returns a dictionary mapping file names in the folder
        to a string of that file's contents.
        Note that you will generally not be running this function; it's used for other functions you will use.
        '''
        files = dict()
        filenames = os.listdir(folder)
        for filename in filenames:
            if "." in filename:
                filename_noext, filename_ext = filename.rsplit(".")
                content = self.file_reader(folder+filename)
                files[filename_noext] = content
        return files
    
# NOTE: the next set of functions are ones you *will* be calling
    def update(self):
        '''
        Checks the txts and jsons folders for new files to import.
        If the filename (w/o extension) is already in the self.txts or self.jsons dictionary,
            then that file will be skipped.
        Any new jsons will be automatically converted to a markov model and added to self.models.
        '''
        to_update = list()
        for idx, folder in enumerate(self.folders[1:]):
            to_update.append((folder, self.data[idx]))
        for folder, dictionary in to_update:
            filenames_u = os.listdir(folder)
            filenames = []
            for filename in filenames_u:
                if "." in filename:
                    filenames.append(filename)
            for filename in filenames:
                filename_noext, filename_ext = filename.rsplit(".")
                if filename_noext not in dictionary.keys() and filename_ext == "txt":
                     dictionary[filename_noext] = self.file_reader(folder+filename)
                elif filename_noext not in dictionary.keys() and filename_ext == "json":
                    dictionary[filename_noext] = self.file_reader(folder+filename)
                    new_model = self.json_interpreter(dictionary[filename_noext])
                    self.models[filename_noext] = new_model
    
    def make_model(self, name, string, pos=False, state_size=2):
        '''
        Receives a string for the name of the new model and a string to make a model from.
        Creates a model and adds a pairing of the new name to the model to self.models.
        Note that you can optionally create a POSified model or change the model's state size
            by passing the optional parameters `pos=True` or `state_size=n` where n is a positive integer.
        Note that this does NOT automatically export the model to self.jsons! You need to do that manually
            using export().
        '''
        if pos == False:
            model = markovify.Text(string, state_size=state_size)
        elif pos == True:
            model = POSifiedText(string, state_size=state_size)
        self.models[name] = model
        
    def combine(self, name, model_names, weights=False):
        '''
        Receives a string for the name of the new model and a list of model names to combine.
        Creates a new combined model and adds a pairing of the new name to the model to self.models.
        Note that you can optionally weight how much each model contributes to the combined model
            by passing the optional parameter `weights=[weight1, weight2, ..., weightN]` where 
            each weight is a positive number and N is the number of models being combined.
            Not passing a weights parameter automatically sets each weight to 1.
        Note that this does NOT automatically export the model to self.jsons! You need to do that manually
            using export().        
        '''
        if weights == False:
            weights = [1 for i in model_names]
        models = list()
        for model_name in model_names:
            models.append(self.models[model_name])
        model_combo = markovify.combine(models, weights)
        self.models[name] = model_combo
        
    def export(self, model_name):
        '''
        Receives a string representing a model name in self.model.keys(), converts the model to json,
            adds it to self.jsons, and then exports that json out to a file with the same name as the model.
        Note that this will overwrite any files with the same name in the jsons folder.
        The reason to make/use jsons is it's much faster than creating the model anew from a string.
        '''
        model = self.models[model_name]
        model_json = model.to_json()
        self.jsons[model_name] = model_json
        with open(self.jsons_folder+model_name+".json",'w') as f:
            f.write(model_json)
    
    def output(self, model_name):
        '''
        Receives a string representing a model name, generates a new sentence using that model, and then returns
            a formatted string made from that sentence that fixes some awkward formatting issues.
        Note that the replacements were largely determined by the files I was using, so you may need to adjust them.
        '''
        model = self.models[model_name]
        sentence = model.make_sentence()
        if sentence != None:
            sentence = sentence.replace(" ,",",").replace(" .",".").replace(r'(?<=[^:]) \.\.\.',"...")\
                .replace(":...",": ...").replace(" ?","?").replace(" !","!").replace(" ;",";")\
                .replace(" :",":").replace("  "," ").replace("   ","  ").replace("\n","")\
                .replace(" )", ")").replace("( ","(").replace(";;",";").replace("::",":")
            try: 
                # fixes apostrophe errors for contractions, e.g. "I 'm" or "do n't"
                patterns = ["[A-Za-z]* '[a-z]", "[A-Za-z]* [a-z]'[a-z]"]
                for pattern in patterns:
                    matches = re.findall(pattern, sentence)
                    for match in matches:
                        match_f = match.replace(" ","")
                        sentence = sentence.replace(match, match_f)
                # fixes apostrophe errors for questions and exclamations, e.g. "Hi!It's" or "Yes?This"
                odd_pattern = "[?!](?=[A-Z])"
                matches = re.findall(odd_pattern, sentence)
                for match in matches:
                    sentence = sentence.replace(match, match+" ")
                if sentence[-1] == " ":
                    sentence = sentence[0:-1]
            except:
                pass
            return sentence
        else:
            return "Sentence could not be generated for '{}', sorry. :( Try again!!".format(model_name)
        
class stageManager(markovManager):
    def __init__(self, root_folder, dupegroup_assocs):
        '''
        Initializes an instance of stageManager given the root folder where data is stored, defined in File Manager,
            and the list of dupes/groups associations (see 2.0 for more info).
        Note that this runs directory_setup(), which means it will check for folders called "txts/", "jsons/", 
            and "txts/scripts/", 
        If these folders do not exist, it will create them.
        These are where your .txt and markovify .jsons should be stored, and where jsons will be written out.
        '''
        super(stageManager, self).__init__(root_folder)
        self.scripts_folder = self.txts_folder+"scripts/"
        self.folders.append(self.scripts_folder)
        self.directory_setup(self.folders)
        self.scripts = super(stageManager, self).folder_to_dict(self.scripts_folder)   
        self.data.append(self.scripts)
        def update(self):
            super(stageManager, self).update()
        self.dupegroups = dupegroup_assocs
        for script in self.scripts:
            dg = None
            for dupegroup in self.dupegroups:
                if script == dupegroup[0]:
                    dg = dupegroup
            if dg == None:
                self.make_diamap(script)
            else:
                self.make_diamap(script, dupes=dg[1], groups=dg[2])
            
    def make_diamap(self, script, dupes=None, groups=None):
        """
        Receives a script and associate it with a dialogue map in self.scripts.
        A dialogue map is a dictionary that maps character names to a list of every instance of their dialogue.
        Note that if there is a dupes dictionary or list of groups names (see 2.0 for more info), this is where
            they come into play.
        """
        dialogue_map = dict()
        script_str = self.scripts[script]
        sentences = script_str.split("\n")
        for sentence in sentences:
            try:
                character, dialogue = sentence.split(": ",1)
                character = character.replace("\"", "").replace("\'","")
                if character not in dialogue_map.keys():
                    dialogue_map[character] = [dialogue]
                else:
                    dialogue_map[character].append(dialogue)
            except:
                pass

        if dupes != None:
            dialogue_map_f = dict()
            for name in dialogue_map.keys():
                if name not in dupes.values():
                    dialogue_map_f[name] = dialogue_map[name]
            for name_d in dupes.keys():
                alias = dupes[name_d]
                alias_dia = dialogue_map[alias]
                dialogue_map_f[name_d].extend(alias_dia)
        else: 
            dialogue_map_f = dialogue_map
        scripts_update = (script_str, dialogue_map_f, groups)
        self.scripts[script] = scripts_update
    
    def character_model(self, model_name, script, character, pos=False, state_size=2):
        """
        Receives a name for a new model to be added to self.models, the name of the script to create a model from,
            and the name of a character to build a model from.
        Note that you can pass it the same optional arguments as you can when creating markovify models.
        """
        out = ""
        for i in self.scripts[script][1][character]:
            out += i + " "
        super(stageManager, self).make_model(model_name, out, pos=False, state_size=2)
        
    def group_model(self, model_name, script, group, pos=False, state_size=2):
        """
        Receives a name for a new model to be added to self.models, the name of the script to create a model from,
            and the name of a group (see 2.0 for more info) to build a model from.
        Note that you can pass it the same optional arguments as you can when creating markovify models.
        """
        out = ""
        characters = self.scripts[script][2][group]
        for character in characters:
            for i in self.scripts[script][1][character]:
                out += i + " "
        super(stageManager, self).make_model(model_name, out, pos=False, state_size=2)
    
    def dialogue_model(self, model_name, script, pos=False, state_size=2):
        """
        Receives a name for a new model to be added to self.models, and the name of the script to create a model from.
        The model will include only the dialogue from the script, not the character tags.
        Note that you can pass it the same optional arguments as you can when creating markovify models.
        """
        out = ""
        for character in self.scripts[script][1].keys():
            for i in self.scripts[script][1][character]:
                out += i + " "
        super(stageManager, self).make_model(model_name, out, pos=False, state_size=2)
        
    def export(self, model_name):
        '''
        Receives a string representing a model name in self.model.keys(), converts the model to json,
            adds it to self.jsons, and then exports that json out to a file with the same name as the model.
        Note that this will overwrite any files with the same name in the jsons folder.
        The reason to make/use jsons is it's much faster than creating the model anew from a string.
        '''
        return super(stageManager, self).export(model_name)
        
    def output(self, model_name):
        '''
        Receives a string representing a model name, generates a new sentence using that model, and then returns
            a formatted string made from that sentence that fixes some awkward formatting issues.
        Note that the replacements were largely determined by the files I was using, so you may need to adjust them.
        '''
        return super(stageManager, self).output(model_name)