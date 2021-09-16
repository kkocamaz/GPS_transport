clearvars
clearvars
close all
clc

% 
% get_tt = load('raw_data\raw_data.mat').get_tt;
% get_tt=sortrows(get_tt,{'arac_id','time'});

% time_1 = datetime({'2019-11-18 08:00:00'});
% time_2 = datetime({'2019-11-18 08:30:00'});


% osrm_out = load('C:\Users\Korhan\Desktop\GitHub\tubitak-gps\comparison\korhan\processing_osrm\osrm_processed.mat').osrm_out;
osrm_out = load('output_data\osrm_output.mat').out;

osrm_out.isUsedAug = false(size(osrm_out,1),1);

segments = load('input_data\osm.mat').osm;

osrm_out.assos_nodes_start = uint64(osrm_out.assos_nodes_start);
osrm_out.assos_nodes_end = uint64(osrm_out.assos_nodes_end);

A = unique(osrm_out.arac_id);
% B = groupcounts(osrm_out.arac_id);
% aug_data = cell2table(cell(0,13), 'VariableNames', {'segment_id', 'start_node', 'end_node', 'calc_length', 'startLat', 'startLon', 'endLat', 'endLon', 'dir', 'AugTime', 'travel_time', 'AugType', 'arac_id'});
aug_data = cell2table(cell(0,11), 'VariableNames', {'segment_id', 'aug_time', 'aug_type', 'arac_id', 'route_id','lat','lon','dir','speed','time_diff','space_diff'});
isUsedAug = [];

% osrm_like = cell2table(cell(0, 2 + size(osrm_out,2)), 'VariableNames' , horzcat(osrm_out.Properties.VariableNames, {'speed', 'travel_time'}));

% leo8b56

% c50o03r size(unique([get_osrm.lat,get_osrm.lon],'rows'))

% zpkvyzx
% zjjvwzc
% z2upzpt
% z272t3t
% 1e8r541
% {'ppvnutx';'uppzv03';'kkyccuy'}

% l50l3qc % 500 speed
% c50o03r 0.81
% w5xcqs0
% 
% for ii = 1:1:size(A,1)
%     if A(ii) == categorical("c63ssl1")
%         break
%     end
% end

ii=1;

for i = ii:1:size(A,1)
%     i
    get_osrm = osrm_out(osrm_out.arac_id == A(i),:);

%     index = (get_osrm.raw_time >= time_1) & (get_osrm.raw_time < time_2) & (get_osrm.confidence >= CONFIDENCE_LEVEL);
%     
%     get_osrm = get_osrm(index,:);
    
    [get_aug, osrm_used] = get_aug_data_v3(get_osrm,segments); %get_aug = get_aug_data_v2(get_osrm,segments);
    
%    
%     [osrm_x,osrm_y] = grn2eqa(get_osrm.lat,get_osrm.lon);
%     figure(200)
%     osrm_routes = unique(get_osrm.route_id);
%     for jj=1:1:length(osrm_routes)
%         index = get_osrm.route_id == osrm_routes(jj) & get_osrm.isMatchedSegments;
%         plot3(osrm_x(index), osrm_y(index), get_osrm.raw_time(index),'-*b')
%         hold on
%     end
%     title(num2str(i));
%     if ~isempty(get_aug)
%         [aug_x,aug_y] = grn2eqa(get_aug.lat,get_aug.lon);
%         figure(200)
%         hold on
%         aug_routes = unique(get_aug.route_id);
%         for jj=1:1:length(aug_routes)
%             r_index = get_aug.route_id == aug_routes(jj);
%             plot3(aug_x(r_index), aug_y(r_index), get_aug.aug_time(r_index),'-ro','MarkerSize',8,'MarkerFaceColor',rand(1,3),'LineWidth', 2)
%             hold on
%         end
%         hold off
%         
%     end
%     xlabel('x - lat');
%     ylabel('y - lon');
%     zlabel('time');
%     grid on
%     grid minor
    
%     osrm_like = vertcat(osrm_like,output2);
    
    aug_data = vertcat(aug_data, get_aug);
    isUsedAug = vertcat(isUsedAug, osrm_used);

%     if ~isempty(get_aug)
%         aug_data = vertcat(aug_data, get_aug);
%     else
%         disp(['error',num2str(i)]);
%     end
    
    
    
%     clf(figure(200))
end

% 
% try
% aug_data = vertcat(aug_data, get_aug_data(osrm_out,segments));
% 
% %     if ~isempty(aug_data)
% %         writetable(aug_data,horzcat('output\aug\aug_',json_list(j).name));
% if isempty(aug_data)
%     fprintf(error_fileID,"%s \n",get_arac);
%     fprintf(error_fileID,"%u \n",j);
%     fprintf(error_fileID,"empty aug matrix \n");
% end
% 
% 
% 
% catch e
%     fprintf(error_fileID,"%s \n",get_arac);
%     fprintf(error_fileID,"%u \n",j);
%     fprintf(error_fileID,"%s \n",e.identifier);
%     fprintf(error_fileID,"%s \n",e.message);
% end


function [output,output2] = get_aug_data_v3(osrm_out,segments)
    % her bir route için yazılmıştır. Route başlangıç ve bitişini dikkate alır.
    
    % for i=...
%     n_route = size(unique(osrm_out.route_id),1);
    route_list = unique(osrm_out.route_id(osrm_out.route_id>=0));
    n_route = size(route_list,1); % to eliminate -99 values which are not confident routes
    C = cell(n_route,2); %1.get_aug 2. extended_aug
    
    for i=1:1:n_route
%         i=0; % ~route_id
        route_id = route_list(i);
        route_loc = (osrm_out.route_id==route_id) & osrm_out.isMatchedSegments;
        
        %dir düzeltmesi
%         route_loc(route_loc>0) = osrm_out.assos_dir(osrm_out.isMatchedSegments) == mode(osrm_out.assos_dir(osrm_out.isMatchedSegments));
%         n_ignore = sum((osrm_out.assos_dir(osrm_out.isMatchedSegments) == mode(osrm_out.assos_dir(osrm_out.isMatchedSegments))) == false);
        
        % bazen rotalar match ediliyor ancak match edilenler segment matchingte yer almıyor böylece route_loc zeros oluyor:
        if sum(route_loc) > 1 % interpolation için en az 2 data lazım
            
            data = osrm_out(route_loc,{'arac_id','raw_time','route_id','assos_segment_id','distance_to_start_node'});
            
            [~,ui] = unique(data.raw_time,'stable');
            data = data(ui,:);
            [~,ui] = unique(data.distance_to_start_node,'stable');
            data = data(ui,:);
            
            if size(data,1) < 2
                continue
            end
            
            if size(unique(osrm_out.assos_dir(route_loc)),1) > 1
                continue
            end
            
            [~,ix] = sort(datenum(data.raw_time)); % sorted olması lazım ama yine de bi sort
            data = data(ix,:);
            
            [~,first_ii]=ismember(data.assos_segment_id(1),segments.segment_id); %ilk segment
            [~,last_ii]=ismember(data.assos_segment_id(end),segments.segment_id); %son segment
            
            
            
            segment_list = segments.segment_id(first_ii:last_ii);
            if isempty(segment_list)
                disp('empty segment list');
                continue
            end
            
            %ilk segmentin başlangıç noktasını reference alarak space axis oluşturma
            space_axis = segments.calc_length(first_ii:last_ii);
            space_axis = cumsum(space_axis) - space_axis;
            
            space_axis(:,2) = segment_list;
            

            [~,b] = ismember(data.assos_segment_id,segment_list);
            
            if sum(b==0)>0
                disp('complex data segment_id');
                continue
            end

            data.data_axis = space_axis(b,1) + data.distance_to_start_node;
            
            
            [xa,~] = ismember(segment_list,data.assos_segment_id);
            
%             ex_ = space_axis(~xa,:); %üstünde data olmayan path segmentleri
            
            
%             data_time = datenum(osrm_out.raw_time(route_loc));
            
%             [~, w] = unique( data_axis, 'stable' );
%             duplicate_indices = setdiff( 1:numel(data_axis), w);
%             [~, w] = unique( data_time, 'stable' );
%             duplicate_indices_2 = setdiff( 1:numel(data_time), w);
%             
%             dup = [duplicate_indices, duplicate_indices_2];
%             if ~isempty(dup)
%                 data_axis(dup) = [];
%                 data_time(dup) = [];
%             end
            
            
            interpolated_time=datetime(interp1(...
                                                  data.data_axis, ...
                                                  datenum(data.raw_time),...
                                                  space_axis(:,1), ...
                                                  'linear','extrap' ...
                                                  ), ...
                                                  'ConvertFrom','datenum');
                                              
            aug_data = table(segment_list, interpolated_time);                                              
                                              
            aug_data.AugType = zeros(size(aug_data,1),1);
            aug_data.AugType(xa)=1; %interpolated segments
            aug_data.AugType(~xa)=2; %exratpolated segments

            aug_data.arac_id = repmat(osrm_out.arac_id(1),size(aug_data,1),1);
            aug_data.route_id = repmat(route_id,size(aug_data,1),1);
            aug_data.lat = segments.startLat(first_ii:last_ii);
            aug_data.lon = segments.startLon(first_ii:last_ii);
            aug_data.dir = segments.dir(first_ii:last_ii);
            aug_data.Properties.VariableNames = {'segment_id', 'aug_time', 'aug_type', 'arac_id', 'route_id','lat','lon','dir'};
            aug_data.speed = [1e-3*diff(space_axis(:,1)) ./ hours(diff(aug_data.aug_time)); NaN];
            aug_data.time_diff = [diff(aug_data.aug_time); NaN];
            aug_data.space_diff = [diff(space_axis(:,1)); NaN];
            
            aug_data(1,:) = []; % route ilk segmentin ilk node'una extrapolate datası siliniyor. (time'da geriye doğru gider)
            
            C{i,1} = aug_data;
            
%             aug_length = size(aug_data,1);
% %             
% %             extended_aug_data = table();
%             extended_aug_data = table(aug_data.arac_id);
%             extended_aug_data.lon = aug_data.lon;
%             extended_aug_data.lat = aug_data.lat;
%             extended_aug_data.raw_time = aug_data.aug_time;
%             extended_aug_data.route_id = aug_data.route_id;
%             extended_aug_data.confidence = NaN(aug_length,1);
%             extended_aug_data.assos_nodes_start = NaN(aug_length,1); % değiştirilebilir.
%             extended_aug_data.assos_nodes_end = NaN(aug_length,1); % değiştirilebilir.
%             extended_aug_data.nodes_to_go = cell(aug_length,1); % değiştirilebilir.
%             
%             route_osrm = osrm_out(route_loc,:);
%             
% %             aux_dir = osrm_out.assos_dir(~isnan(osrm_out.assos_dir));
%             
%             extended_aug_data.assos_dir = repmat(route_osrm.assos_dir(1),aug_length,1);
%             extended_aug_data.assos_segment_id = aug_data.segment_id;
%             extended_aug_data.isMatchedSegments = NaN(aug_length,1);
%             extended_aug_data.distance_to_start_node = zeros(aug_length,1);
%             extended_aug_data.distance_to_end_node = NaN(aug_length,1); % değiştirilebilir.
%             extended_aug_data.speed = aug_data.speed;
%             extended_aug_data.travel_time = aug_data.travel_time;
%             extended_aug_data.Properties.VariableNames{1} = 'arac_id';
%             
% %             osrm_out.speed = NaN(size(osrm_out,1),1);
%             
%             route_osrm.speed = NaN(size(route_osrm,1),1);
%             route_osrm.travel_time = NaN(size(route_osrm,1),1);
% %             route_osrm.route_id = ones(size(route_osrm,1),1) * (i + AUX_ROUTE); % rota id
% %             
% %             [a,b] = ismember(extended_aug_data.assos_segment_id,route_osrm.assos_segment_id);
% % %             [a,b] = ismember(route_osrm.assos_segment_id,extended_aug_data.assos_segment_id);
% %             extended_aug_data.assos_segment_id(b2(b2>0))
% %             route_osrm.speed(b(a)) = extended_aug_data.speed(a);
%             
%             C{i,2} = [route_osrm; extended_aug_data];
            
            osrm_out.isUsedAug(route_loc) = true;
        end
    end
    output = vertcat(C{:,1}); %get_aug
    output2 = osrm_out.isUsedAug;
%     osrm_like = vertcat(C{:,2}); %get_aug
    % hangi datalar kullanıldı
    % https://www.mathworks.com/matlabcentral/answers/375710-find-nearest-value-to-specific-number
    % https://www.mathworks.com/matlabcentral/answers/152301-find-closest-value-in-array
    % https://www.mathworks.com/matlabcentral/answers/85362-find-the-nearest-value

end

function output = get_aug_data_v2(osrm_out,segments)
    % her bir route için yazılmıştır. Route başlangıç ve bitişini dikkate alır.
    
    % for i=...
%     n_route = size(unique(osrm_out.route_id),1);
    n_route = size(unique(osrm_out.route_id(osrm_out.route_id>=0)),1); % to eliminate -99 values which are not confident routes
    C = cell(n_route,1);
    
    for i=0:1:max(osrm_out.route_id(osrm_out.route_id>=0))
%         i=0; % ~route_id
        route_loc = (osrm_out.route_id==i) & osrm_out.isMatchedSegments;
        
        %dir düzeltmesi
%         route_loc(route_loc>0) = osrm_out.assos_dir(osrm_out.isMatchedSegments) == mode(osrm_out.assos_dir(osrm_out.isMatchedSegments));
%         n_ignore = sum((osrm_out.assos_dir(osrm_out.isMatchedSegments) == mode(osrm_out.assos_dir(osrm_out.isMatchedSegments))) == false);
        
        % bazen rotalar match ediliyor ancak match edilenler segment matchingte yer almıyor böylece route_loc zeros oluyor:
        if sum(route_loc) > 1 % interpolation için en az 2 data lazım
            aux = unique(osrm_out.assos_nodes_end(route_loc),'stable');
            
            my_list = unique(vertcat(osrm_out.assos_nodes_start(route_loc),aux(1:end-1)), 'stable');
            
%             my_list(end) = []; == aux(1:end-1) % son datanın üstünde olduğu segmentin end-node'u.
                               % ilerde start_node ile iş yapacağım için çıkarıtıyorum.
                               % start_node ile match yaptığım için not member döndürebiliyor.
                               % path'in içinde varsa nodes to go'dan yine eklenir zaten.
            
            aux_nodes_to_go = osrm_out.nodes_to_go(route_loc);
            
            aux_nodes_to_go{end} = []; % son dataya ait son nodes to go'ya ihtiyaç yok. koridor dışına çırakıyor zaten.
            
            for j=1:1:length(aux_nodes_to_go)
                if ~isempty(aux_nodes_to_go{j})
                    my_list = vertcat(my_list, uint64(transpose(aux_nodes_to_go{j}(2:end))));
                end
%                 a = ismember(aux_nodes_to_go{j},my_list);
%                 my_list = vertcat(my_list,uint64(transpose(aux_nodes_to_go{j}(~a))));
            end
            
            my_list = unique(my_list,'stable');
%             my_list(end) = []; % last node is a endnode of a segment
            
            [~,b] = ismember(my_list , segments.start_node);
            
            
            
            if sum(b == 0) > 0
                % path'te korikor dışına çıkan node'lar var demektir
                % bi olay vardır
                continue % bu foor loop iteration'ı atla (route)
                
%                 my_list(b==0)=[];
%                 b(b==0)=[];
                
                %bütün rotayı salmak yerine b=0 olanları çıkarsam mı acaba
            end
            
            coords = [segments.startLat(b), segments.startLon(b)]; % in my_list sort space
            
            path_segments = segments.segment_id(b);
            [path_segments,pivot] = sort(path_segments); % segmentler komplike network olsa directed path çıkarmam gerekir
            b= b(pivot);
%             segments.segment_id(b)
            my_list = my_list(pivot);
            coords = coords(pivot,:);
            
%             my_list(1) = []; %first node must be the first one - do not want to augment data on it.
            
            segment_axis = segments.calc_length(b);
            
%             segment_axis = cumsum(segment_axis) - segment_axis(1);
            
            segment_axis = cumsum(segment_axis) - segment_axis;
            
            [~,bb] = ismember(osrm_out.assos_nodes_start(route_loc),my_list);
            
            data_axis = osrm_out.distance_to_start_node(route_loc) + segment_axis(bb);
            
            data_time = datenum(osrm_out.raw_time(route_loc));
            
            [~, w] = unique( data_axis, 'stable' );
            duplicate_indices = setdiff( 1:numel(data_axis), w);
            [~, w] = unique( data_time, 'stable' );
            duplicate_indices_2 = setdiff( 1:numel(data_time), w);
            
            dup = [duplicate_indices, duplicate_indices_2];
            if ~isempty(dup)
                data_axis(dup) = [];
                data_time(dup) = [];
            end
            
            
            interpolated_time=datetime(interp1(...
                                                  data_axis, ...
                                                  data_time,...
                                                  segment_axis, ...
                                                  'linear','extrap' ...
                                                  ), ...
                                                  'ConvertFrom','datenum');
                                              
            aug_data = table(my_list, interpolated_time);
%             aug_data.nodes = my_list;
%             aug_data.AugTime = interpolated_time(1:end-1);
%             aug_data.travel_time = diff(interpolated_time);
                                              
                                              
            aug_data.AugType = zeros(size(aug_data,1),1);
            aug_data.AugType(ismember(my_list,osrm_out.assos_nodes_start(route_loc))) = 1; %interpolated segments
            aug_data.AugType(~ismember(my_list,osrm_out.assos_nodes_start(route_loc))) = 2; %exratpolated segments
%             aug_data.distance_from_origin = []; % kaydetmek için gereksiz ?
            aug_data.arac_id = repmat(osrm_out.arac_id(1),size(aug_data,1),1);
            aug_data.route_id = repmat(i,size(aug_data,1),1); % rota id
            aug_data.lat = coords(:,1);
            aug_data.lon = coords(:,2);
            aug_data.Properties.VariableNames = {'nodes', 'aug_time', 'aug_type', 'arac_id', 'route_id','lat','lon'};
            C{i+1,1} = aug_data;
        end
    end
    output = vertcat(C{:});
    
    % hangi datalar kullanıldı
    % https://www.mathworks.com/matlabcentral/answers/375710-find-nearest-value-to-specific-number
    % https://www.mathworks.com/matlabcentral/answers/152301-find-closest-value-in-array
    % https://www.mathworks.com/matlabcentral/answers/85362-find-the-nearest-value

end