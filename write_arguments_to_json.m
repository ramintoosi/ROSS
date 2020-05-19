function write_arguments_to_json(s,filename)
%This functin writes your configuration in a json format. s is a struct.
%fields of s consist of:
%       -root_path = path to the data folder including selective and main
%       folders
%       -lfp_cutoff = the cut-off frequency of lfp filter
%       -lfp_order = the order of butterworth filter for lfp
%       -final_sampling_rate = final sampling rate of signal. sampling rate
%       reduction is done with MATLAB 'decimate' function.
%       -spike_filtr_type = type of filter (used with feval)
%       -spike_filter_order = order of spike filtr
%       -spike_Rp = Rp of spike filter
%       -spike_Rs = Rs of spike filter
%Example:
%s.root_path = "my_path/data/"
%write_arguments_to_json(s,'config.json')

if ~isstruct(s)
    error("s Must be an struct.")
end

% corrections
% s = config_evaluate(s);

txt = jsonencode(s); % encode file to json format

fid = fopen(filename,'w'); % open file to write

if fid > 0 % check wether the file is opened
    fprintf(fid,txt); % print json to file
else
    error('file cannot be opened')
end
fclose(fid);