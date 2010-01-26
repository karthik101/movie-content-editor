clear; close all;

% --------- open files -----------
fid = fopen('panda.srt','r');
out = fopen('mute.txt','wt');
cc = fopen('panda_edit.srt','wt');
% ---------------------------------

% load words we want to filter
badwords = {'skills','mouth','Shashabooey'};

% loop through subtitles
while true
    % --- read caption number -----
    num = fgetl(fid);
    if ~ischar(num), break, end % end of file check
    fprintf(cc,'%s \n',num);
    % ---------------------------------
    
    % --- read time span of caption -----
    times = fgetl(fid);
    fprintf(cc,'%s \n',times);
    % ---------------------------------
    
    % ---- read subtitles and decided whether to edit -------
    reject = false;
    
    tline = fgetl(fid);
    while ~isempty(tline) % blank line between sections
        for i = 1:length(badwords)
            sidx = findstr(tline,badwords{i}); % starting index of bad word
            if ~isempty(sidx)
                eidx = findstr(tline,' '); 
                eidx = min(eidx(eidx > sidx)); % ending index of space after bad word
                tline = [tline(1:sidx-1) '*' tline(eidx:end)];
                reject = true;
            end
        end
        fprintf(cc,'%s \n',tline);
        tline = fgetl(fid);
    end
    
    % add blank line between sections
    fprintf(cc,'\n');
    % ----------------------------------------------------
    
    % --------- convert time to seconds -------------
    if reject
        start = str2num(times(1:2))*3600 + ...
                str2num(times(4:5))*60 + ...
                str2num(times(7:8)) + ...
                str2num(times(10:12))/1000;
            
        finish = str2num(times(18:19))*3600 + ...
                str2num(times(21:22))*60 + ...
                str2num(times(24:25)) + ...
                str2num(times(27:29))/1000;
            
        fprintf(out,'%6.3f \t %6.3f \n',start,finish);
    end
    % -----------------------------------------------
    
    
end
fclose(fid);
fclose(out);
fclose(cc);