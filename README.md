# typora-to-obsidian
Automate some tasks for importing Typora created markdown files with math into Obsidian

# What is this?

A quick personal script I made to migrate my Typora-created, math laden markdown files to [Obsidian](https://obsidian.md/).

It offers mitigations for this problems:

* No suport of HTML elements `<img src="...">` in markdown source with target a relative path
* MathJax years-old bug not honoring `\\` line breaks in math expressions
* No math multiline expression support inside quotations in Obsidian
* `\label` breaks math expressions in Obsidian.

# Fixes

## Images

The script will warn an ignore remote images. Obsidian can't handle <img src...> elements with relative paths. This scrip replaces elements

```
<img src="path" ... style="zoom: 30%;"...>
```
with

```
![|width](path)
```
that opens in Obsidian.

Zoom is parsed and applied to actual size of the image from the image file.

If you want your images centered, you can add the CSS snippet

```
img { display:block; margin-left: auto; margin-right: auto; }
```


## MathJax line breaks

Obsidian renders math with MathJax so it suffers [this](https://github.com/mathjax/MathJax/issues/2312) 2019 bug. The mitigation here is to enclose all displayed math expressions `($$ ... $$)` in a `gathered` environment, so the expressions is transformed into

```
$$\begin{gathered}
...
\end{gathered}$$
```
As released, the script does this to *all* such expressions. Users are invited to fork and enhance it so the fix only applies to expressions containing `\\` line breaks.

## No math multiline expression support inside quotations in Obsidian

Actually Obsidian doesn't support multiline equations in quotations such as this

```
>
> $$ 
> e = mc^2
> f = ma
> $$
>

The mitigation is to transform the quotation into a titleless admonition of type **cite**

````
```ad-cite
title:
e = mc^2 \\
f = ma
```
````

Admonitions are eased with the Admonition community plugin [aq](https://github.com/valentine195/obsidian-admonition).

You can edit the admonition to add a title and add made it collapsible.

If you want citations be of same background color as the main text you can add this CSS snippet

```
.callout[data-callout="cite"] { 
	--callout-icon: Quote; 
	background-color: var(--background-primary);
}
```

## Labels

In math expressions, labels (`\label{...}` latex commands) break Obsidian math expression parser. That unfortunately breaks the `label`,`tag`,`eqref` latex command associations. The script mitigation is to wholly remove `label`s, and only one `tag` command in an expression is taken into account and placed a the end of the expression. Users have to manually have to fix broken `eqref` mentions. 


# Installing

Install a Python environment. 

If needed install the Pillow package

```
pip install pillow
```

# Running

Before running, macking up your markup files directory is recommended.

Run the command with

```
python typora-to-obsidian <directory>
```

The script will walk that directory and subdirectories recursively looking for markdown `.md` files, for instance `name.md`, process it, and produce as result a file suffixed `.obsidian.md`. For instance, `name.obsidian.md`.

With this naming scheme, the script is _idempotent_: The results of running it once or several times are in theory the same. One create an Obsidian vault at the base directory and compare original and transformed results and tweak the script as needed. On the other hand, once one is satisfied with the results, some pesky renaming can be needed that the script does not do.

# Disclaimer

Back your content directory befor to appling this script. Software is provided AS IS, no support is guaranteed and issues/complaints can be discretionally ignored.




