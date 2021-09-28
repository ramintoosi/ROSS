function [commands, error_message] = readBatchFile(file)
error_message = [];
commands = [];
empty = true;
f = fileread(file);
lines = regexp(f, '\r?\n', 'split');
for i = 1:length(lines)
    line = lines(i);
    words = strtrim(split(line, ','));
    if strcmpi(words, '')
        continue;
    else
        empty = false;
        if length(words) < 2
            error_message = [error_message, 'Not enough command words in line ' num2str(i) '. '];
            continue;
        end
        if ~(strcmpi(words(1), 'sort') || strcmpi(words(1), 'detect') || strcmpi(words(1), 'both'))
            error_message = [error_message, 'Not recognized command in line ' num2str(i) '. '];
            continue;
        end
        if (strcmpi(words(1), 'sort') && ~(length(words)==2)) || (~strcmpi(words(1), 'sort') && ~(length(words)==3))
            error_message = [error_message, 'Incorrect number of words in line ' num2str(i) '. '];
            continue;
        end
        [command.path,name,ext] = fileparts(char(words(2)));
        command.filename = [name ext];
        command.process = char(words(1));
        if ~strcmpi(words(1), 'sort')
            command.variable = char(words(3));
        else
            command.variable = '';
        end
        commands = [commands command];
    end
end
if empty
    error_message = [error_message, 'Empty File. '];
end
end