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
  let to = "/vdex-web"
  let b = [{
    disabled: false,
    nuxt: true,
    text: "vdex-web",
    to: to,
  }]
  let woExt = replaceExt(relPath, "")
  if (path.basename(woExt) == "index") {
    woExt = path.dirname(woExt)
  }
  for (let part of woExt.split(path.sep)) {
    to += "/" + part
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
  $("a").each(function(index, elem) {
    let text = $(this).text()
    let href = $(this).attr("href").replace("/", path.sep)
    let woExt = replaceExt(href, "")
    if (path.basename(woExt) == "index") {
      woExt = path.dirname(woExt)
    }
    let joined = path.join(path.dirname(relPath), woExt)
    let to = "/vdex-web/" + joined.replace(path.sep, "/")
    let link = $("<nuxt-link></nuxt-link>")
    link.attr("to", to)
    link.text(text)
    $(this).replaceWith(link)
  })
  let elements = $("body").children().slice(1)
  let s = "<template>\n<div>\n"
  s += "<v-breadcrumbs :items=\"breadcrumbs\" divider=\"/\"></v-breadcrumbs>\n"
  elements.each(function(index, elem) {
    s += $.html($(this))
  })
  s += "</div>\n</template>\n<script lang=\"ts\">\n"
  s += "import { Component, Vue } from \"nuxt-property-decorator\"\n"
  s += "@Component\nexport default class Page extends Vue {\n"
  s += "breadcrumbs: object[] = " + JSON.stringify(breadcrumbs(relPath)) + "\n"
  s += "head() {\nreturn {\ntitle: " + JSON.stringify(title) + "\n}\n}\n"
  s += "}\n</script>\n"
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
