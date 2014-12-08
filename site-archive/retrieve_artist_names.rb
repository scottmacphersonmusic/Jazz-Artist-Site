pattern = />\w+ \w+</
timestamp = Time.now.to_s.gsub(/ /, "_")
archive_file = File.open "catalog_url_list_#{timestamp}.txt", "w"

File.open("./artist_list.txt", "r") do |file|
  file.each_line do |line|
    if pattern =~ line
      name = $~[0]
      formatted_name = name.gsub(/<|>/, "").gsub(/ /, "-").downcase
      archive_file.puts formatted_name
    end
  end
end

archive_file.close
