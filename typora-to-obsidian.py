import sys
import os
import io
import re
from PIL import Image	# pip install pillow

DEFAULT_IMAGE_WIDTH=1000

def get_image_width(image_file_name):
	try:
		img = Image.open(image_file_name)
	except FileNotFoundError: 
		print("ERROR: Image file not found: ", image_file_name)
		return None

	return img.width
		
# e. g.: ...style="zoom: 30%;"...
def get_zoom(line):
	l1 = line.split('style="')
	if len(l1) == 1: return None
	style = l1[1].split('"')[0].strip()
	l2 = list(filter(None, style.split(";")));
	if len(l2) > 1:
		print("ERROR: Unsuported complex style attribute", style)
		return None
	if not style.startswith("zoom:"):
		print("ERROR: Only zoom style supported ", style)
		return None
	zoom_value_string = style.replace("zoom:", "").strip("%;");
	try:
		return int(zoom_value_string)
	except InvalidValue:
		print("ERROR '{0}' invalid numeric zoom value".format(zoom_value_string))
		return None
	
	print("ERROR: shouldn't be here'")
	return None
 
def process_image_line(line):
	image_url = line.split('"')[1]
	if image_url.startswith("http"): 
		print ("WARNING: non-local image ", image_url)
		return line
	original_width = get_image_width(image_url)
	if original_width==None: return line
	zoom = get_zoom(line)
	if zoom == None: zoom = 100
	if original_width==None:
		new_width = DEFAULT_IMAGE_WIDTH
		print ("WARNING: defaulting image '{0}' width to {1}".format(image_url, new_width))

	new_width = int(original_width * zoom / 100)
	
	# widen small images +30% (comment out if not needed)
	new_width += int(new_width*30/100)

	# cap image size to DEFAULT_IMAGE_WIDTH
	new_width = min(new_width, DEFAULT_IMAGE_WIDTH)
	
	return "![|{0}]({1})".format(new_width, image_url)

class Context:
	quoting = False
	displaying_latex = False
	equation_tag = ""

def process_line(line, context):
	# obsidian does not support label/eqref. Delete \label tags 
	if context.displaying_latex and line.count("\\label{") > 0:
			tag_regexp = r"\\label{[^}]+\}"
			line = re.sub(tag_regexp, "", line)

	# MathJax does not support \\ line breaks
	# add 'gathered' environment to displayed math blocks

	# move \tag{} to the end past the gathered environment
	if context.displaying_latex and line.count("\\tag{") > 0:
			tag_regexp = r"\\tag{[^}]+\}"
			context.equation_tag = re.findall(tag_regexp, line)[-1]	# last tag, ignore rest
			line = re.sub(tag_regexp, "", line)
	
	if line.count("$$") == 1:
		if not context.displaying_latex:
			line = line.replace("$$", "$$\\begin{gathered}")
		
		if context.displaying_latex:
			line = line.replace("$$", "\\end{{gathered}}{0}$$".format(context.equation_tag))
			context.equation_tag = ""
			
		context.displaying_latex = not context.displaying_latex

	# obsidian does not support multiline math in quotations but it does in admonitions
	# replace quotations for admonition blocks of type 'cite'
	
	if not context.quoting:
		if line.lstrip().startswith(">"):
			context.quoting = True
			unquoted_line = line.replace(">", "", 1).lstrip();
			line = "```ad-cite\ntitle:\n" + unquoted_line # empty title shows no header
	else:
		if line.lstrip().startswith(">"):
			line = line.replace(">", "", 1).lstrip();
		else:
			context.quoting = False
			line = "```\n" + line

	# obsidian can't handle <img src...> elements with relative paths
	# replace <img src="path" ...> with ![|width](path)
	
	if "<img src=" in line:
		element_regexp = r'<img src="([^>]+)"[^>]*>'
		line = re.sub(element_regexp, lambda x: process_image_line(x.group()), line)
		
		#if in table, quote image pipe chars 
		if line.lstrip()[0] == "|":
			line = "|" + line.lstrip()[1:].replace("[|", r"[\|")

	return line

# kk.md -> kk.obsidian.md
def get_new_file_name(file_path):
	l = file_path.split(".")
	l.insert(-1, "obsidian")
	return ".".join(l)

# convert blah.md file into blah.obsidian.md
def process_md_file(file_path):
	if "obsidian" in file_path: return

	new_file_path = get_new_file_name(file_path)
	print("Processing file {0} -> {1}".format(file_path, new_file_path))

	context = Context()
	context.quoting = False
	context.displaying_latex = False
	context.equation_tag = ""
	
	# read the backup file and rewrite original file
	with \
	io.open(file_path, 'r', encoding="utf-8") as input_file, \
	io.open(new_file_path, 'w', encoding="utf-8") as output_file:
		for line in input_file.readlines():
			output_line = process_line(line.rstrip('\r\n'), context)
			output_file.write(output_line + "\n")
			
	input_file.close()
	output_file.close()

def walk_error_handler(exception_instance):
    print(str(exception_instance))  

# process all md files in directory and subdirectories
def process_directory(directory):
	md_absolute_file_paths = []
	for root, subdirectories, files in os.walk(directory, onerror=walk_error_handler):
		for file in files:
			if os.path.splitext(file)[1] == ".md":
				md_file_path = os.path.join(root, file)
				md_absolute_file_path = os.path.abspath(md_file_path)
				md_absolute_file_paths.append(md_absolute_file_path)
		
	launch_directory = os.getcwd()
	
	# call process_md_file with working directory the one containing the md file
	# so relative paths in md file are true
	for md_absolute_file_path in md_absolute_file_paths:
		subdirectory = os.path.dirname(md_absolute_file_path)
		os.chdir(subdirectory)
		process_md_file(md_absolute_file_path)
		
	os.chdir(launch_directory)

def main():
	if len(sys.argv) != 2:
		print("Directory expected");
		sys.exit(1)
	
	process_directory(sys.argv[1])
	
if __name__ == '__main__':
	main()
