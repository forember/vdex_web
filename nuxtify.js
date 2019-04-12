// vim: set ts=2 sts=2 sw=2 et :
let cheerio = require("cheerio")
let fs = require("fs-extra")
let path = require("path")

let src = path.join(__dirname, "output/localhost:5000")
let dst = path.join(__dirname, "output/vdex-web")

function replaceExt(filePath, ext) {
  return path.join(path.dirname(filePath),
    path.basename(filePath, path.extname(filePath)) + ext)
}

function breadcrumbs(relPath) {
  let to = "/"
  let b = [{
    disabled: false,
    text: "VDex",
    to: to,
  }]
  let woExt = replaceExt(relPath, "")
  if (path.basename(woExt) == "index") {
    woExt = path.dirname(woExt)
  }
  for (let part of woExt.split(path.sep)) {
    to += part + "/"
    b.push({
      disabled: false,
      nuxt: true,
      text: part,
      to: to,
    })
  }
  b[b.length - 1]["disabled"] = true
  return b
}

function convert(relPath, content) {
  let $ = cheerio.load(content)
  let title = $("title").text().replace("|", "-")
  let styles = $("style")
  $("a").each(function(index, elem) {
    let text = $(this).text()
    let href = $(this).attr("href").replace("/", path.sep)
    let woExt = replaceExt(href, "")
    if (path.basename(woExt) == "index") {
      woExt = path.dirname(woExt)
    }
    let joined = path.join(path.dirname(relPath), woExt)
    let to = "/" + joined.replace(path.sep, "/")
    let link  = $("<a></a>")
    link.attr("href", to)
    link.text(text)
    $(this).replaceWith(link)
  })
  let elements = $("body").children().slice(1)
  let s = "<template>\n<div>\n"
  s += "<div>\n"
  for (let crumb of breadcrumbs(relPath)) {
    if (crumb.disabled) {
      let a = $("<span></span>")
      a.text(crumb.text)
      s += $.html(a) + "\n"
    } else {
      let a = $("<a></a>")
      a.attr("href", crumb.to)
      a.text(crumb.text)
      s += $.html(a) + " /\n"
    }
  }
  s += "</div>\n"
  elements.each(function(index, elem) {
    s += $.html($(this))
  })
  s += "</div>\n</template>\n<script lang=\"ts\">\n"
  s += "import { Component, Vue } from \"nuxt-property-decorator\"\n"
  s += "@Component\nexport default class Page extends Vue {\n"
  s += "head() {\nreturn {\ntitle: " + JSON.stringify(title) + "\n} } "
  s += "}\n</script>\n<style>\n"
  styles.each(function(index, elem) {
    s += $(this).html() + "\n"
  })
  s += "\n</style>\n"
  return s
}

function walk(dir) {
  for (let name of fs.readdirSync(dir, "utf8")) {
    let entry = path.join(dir, name)
    if (path.extname(entry) == ".html") {
      let relPath = path.relative(src, entry)
      let contents = fs.readFileSync(entry, "utf8")
      let dstPath = path.join(dst, replaceExt(relPath, ".vue"))
      let dstContents = convert(relPath, contents)
      fs.ensureDirSync(path.dirname(dstPath))
      fs.writeFileSync(dstPath, dstContents, "utf8")
    } else {
      walk(entry)
    }
  }
}

walk(src)
