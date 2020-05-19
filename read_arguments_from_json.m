function config_struct = read_arguments_from_json(config_file)
% Reads arguments written to config file and returns them as an struct

fid = fopen(config_file,'r');
if fid > 0
    txt = fscanf(fid,'%c');
else
    error('config file cannot be opened')
end
fclose(fid);

config_struct = jsondecode(txt);