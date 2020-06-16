function [files] = findRegexFiles(root, subfolderlevel, regexp)
files = [];
sub_folders = {root};
for level = 0:subfolderlevel
    if isempty(sub_folders)
        break;
    end
    sub_sub_folders = [];
    for i = 1:length(sub_folders)
        current_folder = char(sub_folders(i));
        current_files = getRegexFiles(current_folder, regexp);
        for j = 1:length(current_files)
            s.folder = current_folder;
            s.file = current_files(j);
            files = [s files];
        end
        if level < subfolderlevel
            f = dir(current_folder);
            f = f(3:end);
            isfolder = [f.isdir];
            folder_cell = struct2cell(f(isfolder));
            sub_sub_folders = [strcat(folder_cell(2,:), '\', folder_cell(1,:)) sub_sub_folders];
        end
    end
    if level < subfolderlevel
        sub_folders = sub_sub_folders;
    end    
end
end