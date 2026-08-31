--========================================================
-- SIMBOT CHAT & SOCIAL ENGINE (PHASE D)
-- Pure ANSI / Windows-1258 Encoding
--========================================================

SimCityChat = SimCityChat or {}

-- Traditional generic collections for backward compatibility
SimCityChat.chatCollection = {
    "Chao, dong qua nhi!",
    "Them an keo ho lo qua :L",
    "Thang An thieu tien chua tra",
    "Ke nay keo hoi danh no moi duoc",
    "Thang kia co tien day",
    "Hom nay troi mat nhi",
    "Quan chao long ngon qua",
    "Thang nao danh len tao :@",
    "ks = ds",
    "Dang ra! Dang ra!",
    "Co nang kia xinh that",
    "Hu tieu ngon nhi",
    "Tuong Duong nay co gi vui?",
    "Toi bi moc tui roi :L",
    "Het tien roi sao gio?",
    "Duong xa met qua",
    "Tiem vu khi o dau nhi ?",
    "Lam sao luyen skill ta?",
    "Nghe noi Duong Chau dang mua",
    "Thanh Do Lam An Dai Ly ta tim nang",
    "Con Sieu Quang kia dep qua",
    "Bo HKMP kia vip nhi",
    "Mua vo lam mat tich day!!!!",
    "Ai ban bk NMC ko?",
    "Ban Thuy Tinh day!!!",
    "Them nuoc mia qua!!!",
    "Toi khong the het live!",
    "Buon lam chi em oi !",
    "Tao ghim no nay gio",
    "Mua ao nam nay dep that",
    "Tinh hinh Tong Kim co ve cang day",
    "Giang ho don rang co ke thanh lap Dac Nhan Cac",
    "Them banh bao qua"
}

SimCityChat.chatCollectionFight = {
    "Ngon nhao vo!",
    "Duong nay do ta mo!",
    "Mau dong tien bao ke!",
    "Cho xin ti banh mi!",
    "A thang nay lao!",
    "Thang nao dam danh tao!",
    "Dua nao can len tieng!",
    "Nguy hiem! Chay le!",
    "May ha nhoc!",
    "Dua nao dam qua day kiem an!",
    "Anh em dau xong len !",
    "Het no!"
}

SimCityChat.general = SimCityChat.chatCollection
SimCityChat.fighting = SimCityChat.chatCollectionFight

-- Structured Dialogue Trees by Personality Archetype
SimCityChat.personalities = {
    aggressive = {
        idle = {
            "Dua nao dam can duong tao!",
            "Hom nay phai kiem dua nao solo moi duoc.",
            "Nhin gi? Muon an don khong?",
            "Ai qua day tao do sat het!",
            "Bai nay tao bao ke, bien di!"
        },
        fight = {
            "Chet nay con!",
            "Dung lai cho tao!",
            "May ha buoi!",
            "Nem thu chieu nay di!",
            "Khong chay duoc dau!"
        },
        low_hp = {
            "Khon khiep, doi hoi mau tao quay lai tinh so!",
            "Danh len ha, nho mat tao day!",
            "Biet tay tao!"
        },
        kill = {
            "Ga ma thich gay!",
            "Mot mang nua ra di!",
            "Yeu the ma cung doi ra gio!"
        },
        taunt = {
            "Cu nhao vo het day!",
            "Chi co the thoi a?"
        }
    },
    cautious = {
        idle = {
            "Di dung can than, dao nay giang ho hiem ac lam.",
            "Het binh mau roi, phai mua them thoi.",
            "Nen giu khoang cach an toan.",
            "Dung di vao cho dong nguoi."
        },
        fight = {
            "Giu cu ly!",
            "Can than coi chung dinh bua!",
            "Danh tu tu thoi, dung ham ho!",
            "Bom mau lien tuc di!"
        },
        low_hp = {
            "Mau tut nhanh qua, rut lui thoi!",
            "Cuu voi, gan het mau roi!",
            "Phu ve thanh gap!"
        },
        kill = {
            "May qua thoat duoc.",
            "An toan roi, phu!",
            "Khong nen manh dong."
        },
        taunt = {
            "Dung ep nguoi qua dang!"
        }
    },
    friendly = {
        idle = {
            "Chao dai hiep, chuc mot ngay train vui ve!",
            "Anh em ai can pt khong?",
            "Thoi tiet hom nay dep that.",
            "Can giup gi cu goi nhe!"
        },
        fight = {
            "Cung nhau hop luc nao!",
            "Co len anh em!",
            "Ho tro lan nhau nhe!",
            "Tien len!"
        },
        low_hp = {
            "Ai hoi mau giup minh voi!",
            "Gap kho khan roi, anh em tiep vien!",
            "Cam on moi nguoi!"
        },
        kill = {
            "Tuyet voi, lam tot lam anh em!",
            "Chien thang roi!",
            "Cung chia exp nao!"
        },
        taunt = {
            "Chung ta khong co thu oan, xin nhuong duong!"
        }
    },
    chatty = {
        idle = {
            "Nghe noi Tuong Duong sap mo dai hoi vo lam.",
            "Ai mua bi kip 90 khong ta ban re cho!",
            "Hom qua rot duoc cay kiem hoang kim xin lam.",
            "Troi mua buon ngu qua anh em oi.",
            "Dao nay do dac len gia ghe that."
        },
        fight = {
            "Vua danh vua buon chuyen nao!",
            "Chieu nay hoc o dau ma la the!",
            "Chem gio cung phai co phong cach!"
        },
        low_hp = {
            "Oi doi oi dau qua ma oi!",
            "Gay cai xuong suon roi!",
            "Tha cho em lan nay di bac oi!"
        },
        kill = {
            "Day thay ta dinh chua!",
            "Lai them mot chien tich huy hoang de ke lai!",
            "Haha qua da!"
        },
        taunt = {
            "Noi nhieu khong bang lam nhieu dau nha!"
        }
    },
    loner = {
        idle = {
            "...",
            "Yen lang.",
            "Phien phuc.",
            "Tranh ra."
        },
        fight = {
            "Cham dut o day.",
            "Diem huyet!",
            "Tranh duong."
        },
        low_hp = {
            "...",
            "Tam lui."
        },
        kill = {
            "Xong viec.",
            "Kem coi."
        },
        taunt = {
            "Nham chan."
        }
    }
}

-- General helper methods
function SimCityChat:getChat()
    if not self.chatCollection or getn(self.chatCollection) == 0 then
        return "..."
    end
    return self.chatCollection[random(1, getn(self.chatCollection))]
end

function SimCityChat:getChatFight()
    if not self.chatCollectionFight or getn(self.chatCollectionFight) == 0 then
        return "..."
    end
    return self.chatCollectionFight[random(1, getn(self.chatCollectionFight))]
end

-- Smart Personality & Context Chat Lookup
function SimCityChat:GetChatByPersonality(personality, context)
    personality = personality or "friendly"
    context = context or "idle"

    local pTree = self.personalities[personality] or self.personalities["friendly"]
    if not pTree then return self:getChat() end

    local list = pTree[context]
    if not list or getn(list) == 0 then
        list = pTree["idle"] or self.chatCollection
    end

    if not list or getn(list) == 0 then
        return "..."
    end

    return list[random(1, getn(list))]
end

function SimCityChat:GetContextChat(tbNpc, context)
    if not tbNpc then return self:getChat() end
    local personality = tbNpc.personality or "friendly"
    return self:GetChatByPersonality(personality, context)
end
