function [out] = TR_get_distance(x1,x2,a)

    % x1 = [x1 (:,1) = lat , x1 (:,2) = lon ];

    % x2 = [x2 (:,1) = lat , x2 (:,2) = lon ];
    
    % distance from points x1 size(2,N) to points x2 size(N,2)

    % size(output) = (N, N)

    x1 = transpose(x1); % in order to allow broadcasting
    
    aux = 1e3*2*6371.393*asin(sqrt((sind((x2(:,1)-x1(1,:))/2)).^2+cosd(x1(1,:)).*cosd(x2(:,1)).*(sind((x2(:,2)-x1(2,:))/2)).^2));
    switch nargin
        case 2
            out = aux;
        case 3
            % x1 gps points
            % x2 segments
            % e.g x2 is the origin for sign
            out = diag(aux);%.* (transpose(x1(2,:)) > x2(:,2));
    end
end

