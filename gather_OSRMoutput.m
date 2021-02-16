clearvars
close all


segments = load('input_data\osm.mat').osm;
data = jsondecode(fileread('input_data\matches.json'));

CONFIDENCE_LEVEL = 0.7;
time_vector = datetime({'2019-11-18 08:00:00'}):minutes(30):datetime({'2019-11-18 10:00:00'});
route_addition = 0:100:100*(length(time_vector) - 1);

% tt = readtable('08_00-10_00-non-duplicated.csv');
% tt.tarih = [];
% tt.arac_id = categorical(tt.arac_id); %make vehicle ids categorical data type to efficiency
% tt.Properties.VariableNames{5} = 'time';
% 
% % raw data
% % duplicateler kaldırılmamıştır.
% n_duplicates = size(tt(:,2:end),1) - size(unique(tt(:,[2,4,5,6])),1);
% tt=sortrows(tt,{'arac_id','time'}); %ilk olarak araca sonra zamana göre sıralama

% % time numerator
% % araç bazlı zamana göre labellama
% tt.time_num=zeros(size(tt,1),1); %create cloumn
% func_numerator = @(x) {transpose(1:1:length(x))}; 
% 
% [G] = findgroups(tt.arac_id); %category indexes
% tt.time_num = uint64(cell2mat(splitapply(func_numerator,G,G))); %table must be ordered to assign time_numerator correctly





out = cell2table(cell(0,18), 'VariableNames', {'arac_id', 'lon', 'lat', 'raw_time',...
    'route_id','confidence','assos_nodes_start','assos_nodes_end', 'nodes_to_go',...
    'assos_dir', 'assos_segment_id','isMatchedSegments','distance_to_start_node',...
    'distance_to_end_node','distance_from_start','space_diff','time_diff','speed'});

for j=1:1:size(data,1) %unique vehicle
    
    arac_id = data(j).vehicle;
    
%     if categorical({arac_id}) == 's9x08sb'
%         asdad  = 10;
%     end
    [osrm_data,tracep,null_trace,time] = get_tracepoints(data(j).match_result);
    n_data = length(time);
    
    osrm_out = cell2table(repmat({arac_id},n_data,1));
    osrm_out.lon = tracep(:,1);
    osrm_out.lat = tracep(:,2);
    osrm_out.raw_time = time;
    
    
    matching_index = transpose(cell2mat({osrm_data.tracepoints.matchings_index}));
    osrm_out.route_id = matching_index;
    
    confidence = transpose(cell2mat({osrm_data.matchings.confidence}));
    

    osrm_out.confidence = confidence(matching_index+1);
    
    assos_nodes=[]; %aslında dimensionlar belli, değiştir**
    nodes_to_go={};
    for i =1:1:size(osrm_data.matchings,1)
        route_matched = arrayfun(@(x) {transpose(x.annotation.nodes)}, osrm_data.matchings(i).legs(:));
        route_matched{end+1,1}=[route_matched{end,1}(end-1), route_matched{end,1}(end)]; %for last tracepoint
        assos_nodes = vertcat(assos_nodes,cell2mat(cellfun(@(x) {[x(1) x(2)]},route_matched))); %last vertcat because of last tracepoint
        n_nodes_to_go = (cellfun(@(x) {size(x,2)-1} , route_matched)); %-1 since substract first segment
        nodes_to_go = vertcat(nodes_to_go, cellfun(@(x) {x(2:end)},cellfun(@(x,y) {x(end-y:end)},route_matched,n_nodes_to_go))); %ilk olarak end-y:end çektim sonra x(2):end* yaptım
    end
    
    nodes_to_go((cellfun(@(x) size(x,2),nodes_to_go) == 1))={[]};
    
    osrm_out.assos_nodes_start = assos_nodes(:,1);
    osrm_out.assos_nodes_end = assos_nodes(:,2);
    osrm_out.nodes_to_go = cell(size(osrm_out,1),1); % cell
    osrm_out.nodes_to_go = nodes_to_go;
    
    [loc1,loc2]=ismember([osrm_out.assos_nodes_start,osrm_out.assos_nodes_end],[segments.start_node,segments.end_node],'rows');
    
    osrm_out.assos_dir = NaN(size(osrm_out,1),1);
    osrm_out.assos_dir(loc1) = segments.dir(nonzeros(loc2));
    
    osrm_out.assos_segment_id = NaN(size(osrm_out,1),1); % SEGMENTS THAT ARE OUT OF INTEREST -> -1 . E.G. HAYMANA YOLU (not matched with polatlı-ankara osm segments)
    osrm_out.assos_segment_id(loc1) = segments.segment_id(nonzeros(loc2)); % NOTE: NODE NUMBLERI INTEGERA ÇEVİR NaNLARDAN VAZGEÇ SIFIR YAP.**
    
    osrm_out.isMatchedSegments=false(size(osrm_out,1),1);
    osrm_out.isMatchedSegments(loc1)=true;
    
    osrm_out.distance_to_start_node = NaN(size(osrm_out,1),1);
    osrm_out.distance_to_start_node(loc1) = diag(TR_get_distance([osrm_out.lat(loc1), osrm_out.lon(loc1)],[segments.startLat(nonzeros(loc2)), segments.startLon(nonzeros(loc2))]));
    
    osrm_out.distance_to_end_node = NaN(size(osrm_out,1),1);
    osrm_out.distance_to_end_node(loc1) = diag(TR_get_distance([osrm_out.lat(loc1), osrm_out.lon(loc1)],[segments.endLat(nonzeros(loc2)), segments.endLon(nonzeros(loc2))]));
    
    osrm_out.Properties.VariableNames{1} = 'arac_id';
    osrm_out.arac_id = categorical(osrm_out.arac_id);
    
    [~,b] = ismember(osrm_out.assos_segment_id,segments.segment_id);
    osrm_out.distance_from_start = NaN(size(osrm_out,1),1);
    osrm_out.distance_from_start(loc1) = segments.distance_from_start(nonzeros(loc2)) + osrm_out.distance_to_start_node(loc1);
    
    osrm_out.space_diff = NaN(size(osrm_out,1),1);
    osrm_out.time_diff = NaN(size(osrm_out,1),1);
    osrm_out.speed = NaN(size(osrm_out,1),1);
    
    route_list = unique(osrm_out.route_id);
    for z=1:1:length(route_list)
%         get_data = matched(matched.arac_id == arac_list(i) & matched.route_id == route_list(j),:).speed;
%         get_data = get_arac(get_arac.route_id == route_list(j),:);
%         matched(matched.arac_id == arac_list(i) & matched.route_id == route_list(j),:).speed(1:end-1) = 1e-3*diff(matched(matched.arac_id == arac_list(i) & matched.route_id == route_list(j),:).distance_from_start) ./ hours(diff(matched(matched.arac_id == arac_list(i) & matched.route_id == route_list(j),:).raw_time));
        index = osrm_out.route_id == route_list(z);

        osrm_out(index, :).space_diff(1:end-1) = diff(osrm_out.distance_from_start(index));
        osrm_out(index, :).time_diff(1:end-1) = hours(diff(osrm_out.raw_time(index)));
        osrm_out(index,:).speed = 1e-3 * osrm_out(index, :).space_diff ./ osrm_out(index, :).time_diff;
    end
%     
%     osrm_out.space_diff = NaN(size(osrm_out,1),1);
%     osrm_out.space_diff(1:end-1) = diff(osrm_out.distance_from_start);
%     
%     osrm_out.time_diff = NaN(size(osrm_out,1),1);
%     osrm_out.time_diff(1:end-1) = hours(diff(osrm_out.raw_time));
%     
%     osrm_out.speed = 1e-3 * osrm_out.space_diff ./ osrm_out.time_diff;
    
% %     %baştaki sıfırları siler
% %     flag = true;
% %     while flag && size(osrm_out,1) > 0
% %         if osrm_out.isMatchedSegments(1) == 0
% %             osrm_out(1,:) = [];
% %         else
% %             flag = false;
% %         end
% %     end
% %     
% %     f = osrm_out.isMatchedSegments == 0;
% %     df = diff(f);
% %     df= [0; df];
% %     
% %     %arka arkaya 2 sıfır diziliminin 2. sıfırını siler
% %     %geriye tek sıfırlar kalır
% %     % tek sıfırlar rota parçalama yeri olarak belirlenir.
% %     osrm_out(f == 1 & df == 0, :) = [];
% %     
% %     f2 = find(osrm_out.isMatchedSegments == 0);
% %     f2 = [1; f2];
% %     
% %     %tek sıfırların olduğu yerlerden itibaren rota_id'ye 1 eklenir
% %     %var olan rota parçalanmış olur.
% %     for iii=1:1:(length(f2) - 1)
% %         osrm_out.route_id(f2(iii):end) = osrm_out.route_id(f2(iii):end) + 1;
% %     end
% %     
% %     % en son tek sıfırlar da silinir.
% %     osrm_out(f2(2:end),:) = [];


    out = vertcat(out, osrm_out);
end



not_confident = sum((out.confidence < CONFIDENCE_LEVEL));
out((out.confidence < CONFIDENCE_LEVEL),:) = [];

out = sortrows(out,{'arac_id','raw_time'});


for i = 1:1:(length(time_vector) - 1)
    time_1 = time_vector(i);
    time_2 = time_vector(i + 1);
    
    out((out.raw_time >= time_1) & (out.raw_time < time_2),:).route_id = out((out.raw_time >= time_1) & (out.raw_time < time_2),:).route_id + route_addition(i);
end


function [out,out2,out3,out4] = get_tracepoints(input)
    if (isstruct(input.tracepoints))
        %no need to arrange
        %because input.tracepoints does not contain null data.
        %therefore it is struct type.
        out = input;
        out2 = cell2mat(arrayfun(@(x) {transpose(x.location)},input.tracepoints));
        out3 = false(size(input.tracepoints,1),1);
        out4 = transpose(datetime({input.tracepoints(:).tarih},'InputFormat','yyyyMMddHHmmss'));
    elseif (iscell(input.tracepoints))
        %need to arrange
        %because input.tracepoints contains null data. Therefore,
        %it is in cell data type.
        empty_vector_1 = cellfun(@isempty,input.tracepoints(:));
%         display([inputname(1), ' null tracepoints ',num2str(sum(empty_vector_1))]);
        input.tracepoints(empty_vector_1)=[];
        
        temp = input.tracepoints; %getting cell 
        input=rmfield(input,'tracepoints'); %deleting tracepoints field of struct
        
        for i=1:1:size(temp,1)
            input.tracepoints(i,1)=temp{i}; %assigning structs to tracepoints field [temp{:}] ??
        end
        out = input;
        out2 = cell2mat(arrayfun(@(x) {transpose(x.location)},input.tracepoints));
        out3 = empty_vector_1;
        out4 = transpose(datetime({input.tracepoints(:).tarih},'InputFormat','yyyyMMddHHmmss'));
    else
        error('undefined tracepoints data type')
    end
end