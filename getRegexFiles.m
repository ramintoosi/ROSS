function match_files = getRegexFiles(path, regex)
% files = dir([path '/*.mat']);
files = dir(path);
names = {files.name};
match_indices = ~cellfun(@isempty, regexp(names, regex, 'match', 'once'));
match_files = names(match_indices);
end
        