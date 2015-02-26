require "httparty"
timestamp = Time.now.to_s.gsub(/ /, "_")

url_filename = ARGV[0]

def url_maker(name)
  "http://jazzdisco.org/#{name}/catalog"
end

url_file = File.open "./#{url_filename}", "r"
archive_dirname = "album_archive_#{timestamp}"

`mkdir #{archive_dirname}`

url_file.each_line do |line|
  line.gsub!(/\n/, "")
  archive_file_name = "./#{archive_dirname}/#{line}.html"
  archive_file = File.open archive_file_name, "w"

  url = url_maker(line)
  puts url

  response = HTTParty.get url
  if response.code != 200
    raise "Could not fetch page at #{line}"
  else
    archive_file.puts response.body
  end

  archive_file.close
end

url_file.close
