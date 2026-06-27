import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.sql.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.Vector;



public class RPGGameSystem {
    public static void main(String[] args) {
        // 设置 Swing 界面风格为系统默认
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception ignored) {}
        SwingUtilities.invokeLater(LoginFrame::new);
    }
}

// ==================== 数据库工具 ====================
class DBUtil {
    private static final String URL = "jdbc:mysql://localhost:3306/rpg_system?useSSL=false&serverTimezone=UTC&characterEncoding=utf8";
    private static final String USER = "root";       // <-- 改成你的 MySQL 用户名
    private static final String PASSWORD = "123456"; // <-- 改成你的 MySQL 密码

    static {
        try {
            Class.forName("com.mysql.cj.jdbc.Driver");
        } catch (ClassNotFoundException e) {
            throw new RuntimeException("MySQL 驱动加载失败，请检查 mysql-connector-java 是否已添加到项目", e);
        }
    }

    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, USER, PASSWORD);
    }

    public static void close(Connection conn, Statement stmt, ResultSet rs) {
        try { if (rs != null) rs.close(); } catch (Exception ignored) {}
        try { if (stmt != null) stmt.close(); } catch (Exception ignored) {}
        try { if (conn != null) conn.close(); } catch (Exception ignored) {}
    }
}

// ==================== 接口 ====================
interface GameCharacter {
    String getName();
    void setName(String name);
    int getLevel();
    void setLevel(int level);
    int getHp();
    void setHp(int hp);
    int getAttackPower();
    void setAttackPower(int attackPower);
    void attack();
    void defend();
    void levelUp();
    String getInfo();
}

// ==================== 实体类：战士 ====================
class Warrior implements GameCharacter {
    private String name;
    private int level;
    private int hp;
    private int attackPower;
    private int defensePower;
    private String weaponType;

    public Warrior() {}
    public Warrior(String name, int level, int hp, int attackPower, int defensePower, String weaponType) {
        this.name = name; this.level = level; this.hp = hp; this.attackPower = attackPower;
        this.defensePower = defensePower; this.weaponType = weaponType;
    }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public int getLevel() { return level; }
    public void setLevel(int level) { this.level = level; }
    public int getHp() { return hp; }
    public void setHp(int hp) { this.hp = hp; }
    public int getAttackPower() { return attackPower; }
    public void setAttackPower(int attackPower) { this.attackPower = attackPower; }

    public int getDefensePower() { return defensePower; }
    public void setDefensePower(int defensePower) { this.defensePower = defensePower; }
    public String getWeaponType() { return weaponType; }
    public void setWeaponType(String weaponType) { this.weaponType = weaponType; }

    public void attack() {
        JOptionPane.showMessageDialog(null, "⚔️ " + name + " 挥舞" + weaponType + "造成" + attackPower + "点物理伤害！");
    }
    public void defend() {
        JOptionPane.showMessageDialog(null, "🛡️ " + name + " 举起盾牌，防御力" + defensePower + "！");
    }
    public void levelUp() {
        level++; hp += 50; attackPower += 10; defensePower += 8;
    }
    public String getInfo() {
        return String.format("[战士] %s | Lv.%d | HP:%d | 攻击:%d | 防御:%d | 武器:%s",
                name, level, hp, attackPower, defensePower, weaponType);
    }

    public String toString() {
        return "Warrior{name='" + name + "', level=" + level + ", hp=" + hp + ", attackPower=" + attackPower
                + ", defensePower=" + defensePower + ", weaponType='" + weaponType + "'}";
    }
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Warrior w = (Warrior) o;
        return level == w.level && hp == w.hp && attackPower == w.attackPower && defensePower == w.defensePower
                && Objects.equals(name, w.name) && Objects.equals(weaponType, w.weaponType);
    }
    public int hashCode() {
        return Objects.hash(name, level, hp, attackPower, defensePower, weaponType);
    }
}

// ==================== 实体类：法师 ====================
class Mage implements GameCharacter {
    private String name;
    private int level;
    private int hp;
    private int attackPower;
    private int mana;
    private int spellPower;

    public Mage() {}
    public Mage(String name, int level, int hp, int attackPower, int mana, int spellPower) {
        this.name = name; this.level = level; this.hp = hp; this.attackPower = attackPower;
        this.mana = mana; this.spellPower = spellPower;
    }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public int getLevel() { return level; }
    public void setLevel(int level) { this.level = level; }
    public int getHp() { return hp; }
    public void setHp(int hp) { this.hp = hp; }
    public int getAttackPower() { return attackPower; }
    public void setAttackPower(int attackPower) { this.attackPower = attackPower; }

    public int getMana() { return mana; }
    public void setMana(int mana) { this.mana = mana; }
    public int getSpellPower() { return spellPower; }
    public void setSpellPower(int spellPower) { this.spellPower = spellPower; }

    public void attack() {
        if (mana >= 20) {
            mana -= 20;
            int dmg = attackPower + spellPower;
            JOptionPane.showMessageDialog(null, "🔮 " + name + " 释放魔法造成" + dmg + "点伤害！剩余法力:" + mana);
        } else {
            JOptionPane.showMessageDialog(null, "❌ " + name + " 法力不足！");
        }
    }
    public void defend() {
        mana -= 10;
        JOptionPane.showMessageDialog(null, "🔰 " + name + " 施展魔法护盾！剩余法力:" + mana);
    }
    public void levelUp() {
        level++; hp += 30; attackPower += 8; mana += 50; spellPower += 15;
    }
    public String getInfo() {
        return String.format("[法师] %s | Lv.%d | HP:%d | 攻击:%d | 法力:%d | 法强:%d",
                name, level, hp, attackPower, mana, spellPower);
    }

    public String toString() {
        return "Mage{name='" + name + "', level=" + level + ", hp=" + hp + ", attackPower=" + attackPower
                + ", mana=" + mana + ", spellPower=" + spellPower + "}";
    }
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Mage m = (Mage) o;
        return level == m.level && hp == m.hp && attackPower == m.attackPower && mana == m.mana
                && spellPower == m.spellPower && Objects.equals(name, m.name);
    }
    public int hashCode() {
        return Objects.hash(name, level, hp, attackPower, mana, spellPower);
    }
}

// ==================== 实体类：弓箭手 ====================
class Archer implements GameCharacter {
    private String name;
    private int level;
    private int hp;
    private int attackPower;
    private int arrowCount;
    private int range;

    public Archer() {}
    public Archer(String name, int level, int hp, int attackPower, int arrowCount, int range) {
        this.name = name; this.level = level; this.hp = hp; this.attackPower = attackPower;
        this.arrowCount = arrowCount; this.range = range;
    }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public int getLevel() { return level; }
    public void setLevel(int level) { this.level = level; }
    public int getHp() { return hp; }
    public void setHp(int hp) { this.hp = hp; }
    public int getAttackPower() { return attackPower; }
    public void setAttackPower(int attackPower) { this.attackPower = attackPower; }

    public int getArrowCount() { return arrowCount; }
    public void setArrowCount(int arrowCount) { this.arrowCount = arrowCount; }
    public int getRange() { return range; }
    public void setRange(int range) { this.range = range; }

    public void attack() {
        if (arrowCount > 0) {
            arrowCount--;
            JOptionPane.showMessageDialog(null, "🏹 " + name + " 射出一箭(" + range + "米)造成" + attackPower + "点伤害！剩余箭矢:" + arrowCount);
        } else {
            JOptionPane.showMessageDialog(null, "❌ " + name + " 箭矢耗尽！");
        }
    }
    public void defend() {
        JOptionPane.showMessageDialog(null, "💨 " + name + " 后撤拉开距离！");
    }
    public void levelUp() {
        level++; hp += 35; attackPower += 12; arrowCount += 20;
    }
    public String getInfo() {
        return String.format("[弓箭手] %s | Lv.%d | HP:%d | 攻击:%d | 箭矢:%d | 射程:%d米",
                name, level, hp, attackPower, arrowCount, range);
    }

    public String toString() {
        return "Archer{name='" + name + "', level=" + level + ", hp=" + hp + ", attackPower=" + attackPower
                + ", arrowCount=" + arrowCount + ", range=" + range + "}";
    }
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Archer a = (Archer) o;
        return level == a.level && hp == a.hp && attackPower == a.attackPower && arrowCount == a.arrowCount
                && range == a.range && Objects.equals(name, a.name);
    }
    public int hashCode() {
        return Objects.hash(name, level, hp, attackPower, arrowCount, range);
    }
}

// ==================== 实体类：刺客 ====================
class Assassin implements GameCharacter {
    private String name;
    private int level;
    private int hp;
    private int attackPower;
    private double criticalRate;
    private int stealthCount;

    public Assassin() {}
    public Assassin(String name, int level, int hp, int attackPower, double criticalRate, int stealthCount) {
        this.name = name; this.level = level; this.hp = hp; this.attackPower = attackPower;
        this.criticalRate = criticalRate; this.stealthCount = stealthCount;
    }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public int getLevel() { return level; }
    public void setLevel(int level) { this.level = level; }
    public int getHp() { return hp; }
    public void setHp(int hp) { this.hp = hp; }
    public int getAttackPower() { return attackPower; }
    public void setAttackPower(int attackPower) { this.attackPower = attackPower; }

    public double getCriticalRate() { return criticalRate; }
    public void setCriticalRate(double criticalRate) { this.criticalRate = criticalRate; }
    public int getStealthCount() { return stealthCount; }
    public void setStealthCount(int stealthCount) { this.stealthCount = stealthCount; }

    public void attack() {
        if (stealthCount > 0) {
            stealthCount--;
            boolean isCrit = Math.random() < criticalRate;
            int dmg = isCrit ? attackPower * 2 : attackPower;
            JOptionPane.showMessageDialog(null, (isCrit ? "💥暴击" : "⚔️背刺") + " " + name + " 造成" + dmg + "点伤害！剩余隐身:" + stealthCount);
        } else {
            JOptionPane.showMessageDialog(null, "⚔️ " + name + " 普通攻击" + attackPower + "点伤害");
        }
    }
    public void defend() {
        if (stealthCount > 0) {
            stealthCount--;
            JOptionPane.showMessageDialog(null, "👤 " + name + " 进入隐身！剩余:" + stealthCount);
        } else {
            JOptionPane.showMessageDialog(null, "❌ " + name + " 无法隐身！");
        }
    }
    public void levelUp() {
        level++; hp += 40; attackPower += 15; criticalRate = Math.min(1.0, criticalRate + 0.05); stealthCount += 2;
    }
    public String getInfo() {
        return String.format("[刺客] %s | Lv.%d | HP:%d | 攻击:%d | 暴击:%.0f%% | 隐身:%d",
                name, level, hp, attackPower, criticalRate * 100, stealthCount);
    }

    public String toString() {
        return "Assassin{name='" + name + "', level=" + level + ", hp=" + hp + ", attackPower=" + attackPower
                + ", criticalRate=" + criticalRate + ", stealthCount=" + stealthCount + "}";
    }
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Assassin a = (Assassin) o;
        return level == a.level && hp == a.hp && attackPower == a.attackPower
                && Double.compare(a.criticalRate, criticalRate) == 0 && stealthCount == a.stealthCount
                && Objects.equals(name, a.name);
    }
    public int hashCode() {
        return Objects.hash(name, level, hp, attackPower, criticalRate, stealthCount);
    }
}

// ==================== 实体类：牧师 ====================
class Priest implements GameCharacter {
    private String name;
    private int level;
    private int hp;
    private int attackPower;
    private int healPower;
    private int faithValue;

    public Priest() {}
    public Priest(String name, int level, int hp, int attackPower, int healPower, int faithValue) {
        this.name = name; this.level = level; this.hp = hp; this.attackPower = attackPower;
        this.healPower = healPower; this.faithValue = faithValue;
    }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public int getLevel() { return level; }
    public void setLevel(int level) { this.level = level; }
    public int getHp() { return hp; }
    public void setHp(int hp) { this.hp = hp; }
    public int getAttackPower() { return attackPower; }
    public void setAttackPower(int attackPower) { this.attackPower = attackPower; }

    public int getHealPower() { return healPower; }
    public void setHealPower(int healPower) { this.healPower = healPower; }
    public int getFaithValue() { return faithValue; }
    public void setFaithValue(int faithValue) { this.faithValue = faithValue; }

    public void attack() {
        if (faithValue >= 15) {
            faithValue -= 15;
            JOptionPane.showMessageDialog(null, "✨ " + name + " 释放圣光造成" + attackPower + "点伤害！信仰:" + faithValue);
        } else {
            JOptionPane.showMessageDialog(null, "❌ " + name + " 信仰不足！");
        }
    }
    public void defend() {
        if (faithValue >= 10) {
            faithValue -= 10; hp += healPower;
            JOptionPane.showMessageDialog(null, "💚 " + name + " 治疗自己+" + healPower + "HP！当前:" + hp + " 信仰:" + faithValue);
        } else {
            JOptionPane.showMessageDialog(null, "❌ " + name + " 信仰不足！");
        }
    }
    public void levelUp() {
        level++; hp += 45; attackPower += 6; healPower += 20; faithValue += 40;
    }
    public String getInfo() {
        return String.format("[牧师] %s | Lv.%d | HP:%d | 攻击:%d | 治疗:%d | 信仰:%d",
                name, level, hp, attackPower, healPower, faithValue);
    }

    public String toString() {
        return "Priest{name='" + name + "', level=" + level + ", hp=" + hp + ", attackPower=" + attackPower
                + ", healPower=" + healPower + ", faithValue=" + faithValue + "}";
    }
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Priest p = (Priest) o;
        return level == p.level && hp == p.hp && attackPower == p.attackPower
                && healPower == p.healPower && faithValue == p.faithValue
                && Objects.equals(name, p.name);
    }
    public int hashCode() {
        return Objects.hash(name, level, hp, attackPower, healPower, faithValue);
    }
}

// ==================== 数据访问层 ====================
class CharacterDao {
    public void add(GameCharacter c) {
        String sql = "INSERT INTO characters (name,char_type,level,hp,attack_power,defense_power,weapon_type,mana,spell_power,arrow_count,range_val,critical_rate,stealth_count,heal_power,faith_value) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";
        try (Connection conn = DBUtil.getConnection(); PreparedStatement ps = conn.prepareStatement(sql)) {
            setCommonParams(ps, c);
            ps.executeUpdate();
        } catch (SQLException e) {
            JOptionPane.showMessageDialog(null, "添加失败：" + e.getMessage());
        }
    }

    public void deleteByName(String name) {
        String sql = "DELETE FROM characters WHERE name=?";
        try (Connection conn = DBUtil.getConnection(); PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, name);
            ps.executeUpdate();
        } catch (SQLException e) { e.printStackTrace(); }
    }

    public void update(GameCharacter c) {
        String sql = "UPDATE characters SET level=?,hp=?,attack_power=?,defense_power=?,weapon_type=?,mana=?,spell_power=?,arrow_count=?,range_val=?,critical_rate=?,stealth_count=?,heal_power=?,faith_value=? WHERE name=?";
        try (Connection conn = DBUtil.getConnection(); PreparedStatement ps = conn.prepareStatement(sql)) {
            int i = 1;
            ps.setInt(i++, c.getLevel()); ps.setInt(i++, c.getHp()); ps.setInt(i++, c.getAttackPower());
            if (c instanceof Warrior) {
                Warrior w = (Warrior) c;
                ps.setInt(i++, w.getDefensePower()); ps.setString(i++, w.getWeaponType());
                ps.setInt(i++, 0); ps.setInt(i++, 0); ps.setInt(i++, 0); ps.setInt(i++, 0);
                ps.setDouble(i++, 0); ps.setInt(i++, 0); ps.setInt(i++, 0); ps.setInt(i++, 0);
            } else if (c instanceof Mage) {
                Mage m = (Mage) c;
                ps.setInt(i++, 0); ps.setString(i++, "");
                ps.setInt(i++, m.getMana()); ps.setInt(i++, m.getSpellPower());
                ps.setInt(i++, 0); ps.setInt(i++, 0);
                ps.setDouble(i++, 0); ps.setInt(i++, 0); ps.setInt(i++, 0); ps.setInt(i++, 0);
            } else if (c instanceof Archer) {
                Archer a = (Archer) c;
                ps.setInt(i++, 0); ps.setString(i++, "");
                ps.setInt(i++, 0); ps.setInt(i++, 0);
                ps.setInt(i++, a.getArrowCount()); ps.setInt(i++, a.getRange());
                ps.setDouble(i++, 0); ps.setInt(i++, 0); ps.setInt(i++, 0); ps.setInt(i++, 0);
            } else if (c instanceof Assassin) {
                Assassin a = (Assassin) c;
                ps.setInt(i++, 0); ps.setString(i++, "");
                ps.setInt(i++, 0); ps.setInt(i++, 0);
                ps.setInt(i++, 0); ps.setInt(i++, 0);
                ps.setDouble(i++, a.getCriticalRate()); ps.setInt(i++, a.getStealthCount());
                ps.setInt(i++, 0); ps.setInt(i++, 0);
            } else if (c instanceof Priest) {
                Priest p = (Priest) c;
                ps.setInt(i++, 0); ps.setString(i++, "");
                ps.setInt(i++, 0); ps.setInt(i++, 0);
                ps.setInt(i++, 0); ps.setInt(i++, 0);
                ps.setDouble(i++, 0); ps.setInt(i++, 0);
                ps.setInt(i++, p.getHealPower()); ps.setInt(i++, p.getFaithValue());
            }
            ps.setString(i++, c.getName());
            ps.executeUpdate();
        } catch (SQLException e) { e.printStackTrace(); }
    }

    public List<GameCharacter> findAll() {
        List<GameCharacter> list = new ArrayList<>();
        try (Connection conn = DBUtil.getConnection(); Statement stmt = conn.createStatement(); ResultSet rs = stmt.executeQuery("SELECT * FROM characters")) {
            while (rs.next()) list.add(mapRow(rs));
        } catch (SQLException e) { e.printStackTrace(); }
        return list;
    }

    public Optional<GameCharacter> findByName(String name) {
        String sql = "SELECT * FROM characters WHERE name=?";
        try (Connection conn = DBUtil.getConnection(); PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, name);
            ResultSet rs = ps.executeQuery();
            if (rs.next()) return Optional.of(mapRow(rs));
        } catch (SQLException e) { e.printStackTrace(); }
        return Optional.empty();
    }

    public List<GameCharacter> findByType(String type) {
        List<GameCharacter> list = new ArrayList<>();
        String sql = "SELECT * FROM characters WHERE char_type=?";
        try (Connection conn = DBUtil.getConnection(); PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, type);
            ResultSet rs = ps.executeQuery();
            while (rs.next()) list.add(mapRow(rs));
        } catch (SQLException e) { e.printStackTrace(); }
        return list;
    }

    private void setCommonParams(PreparedStatement ps, GameCharacter c) throws SQLException {
        int i = 1;
        ps.setString(i++, c.getName());
        ps.setString(i++, c.getClass().getSimpleName().toLowerCase());
        ps.setInt(i++, c.getLevel()); ps.setInt(i++, c.getHp()); ps.setInt(i++, c.getAttackPower());
        if (c instanceof Warrior) {
            Warrior w = (Warrior) c;
            ps.setInt(i++, w.getDefensePower()); ps.setString(i++, w.getWeaponType());
            ps.setInt(i++, 0); ps.setInt(i++, 0); ps.setInt(i++, 0); ps.setInt(i++, 0);
            ps.setDouble(i++, 0); ps.setInt(i++, 0); ps.setInt(i++, 0); ps.setInt(i++, 0);
        } else if (c instanceof Mage) {
            Mage m = (Mage) c;
            ps.setInt(i++, 0); ps.setString(i++, "");
            ps.setInt(i++, m.getMana()); ps.setInt(i++, m.getSpellPower());
            ps.setInt(i++, 0); ps.setInt(i++, 0);
            ps.setDouble(i++, 0); ps.setInt(i++, 0); ps.setInt(i++, 0); ps.setInt(i++, 0);
        } else if (c instanceof Archer) {
            Archer a = (Archer) c;
            ps.setInt(i++, 0); ps.setString(i++, "");
            ps.setInt(i++, 0); ps.setInt(i++, 0);
            ps.setInt(i++, a.getArrowCount()); ps.setInt(i++, a.getRange());
            ps.setDouble(i++, 0); ps.setInt(i++, 0); ps.setInt(i++, 0); ps.setInt(i++, 0);
        } else if (c instanceof Assassin) {
            Assassin a = (Assassin) c;
            ps.setInt(i++, 0); ps.setString(i++, "");
            ps.setInt(i++, 0); ps.setInt(i++, 0);
            ps.setInt(i++, 0); ps.setInt(i++, 0);
            ps.setDouble(i++, a.getCriticalRate()); ps.setInt(i++, a.getStealthCount());
            ps.setInt(i++, 0); ps.setInt(i++, 0);
        } else if (c instanceof Priest) {
            Priest p = (Priest) c;
            ps.setInt(i++, 0); ps.setString(i++, "");
            ps.setInt(i++, 0); ps.setInt(i++, 0);
            ps.setInt(i++, 0); ps.setInt(i++, 0);
            ps.setDouble(i++, 0); ps.setInt(i++, 0);
            ps.setInt(i++, p.getHealPower()); ps.setInt(i++, p.getFaithValue());
        }
    }

    private GameCharacter mapRow(ResultSet rs) throws SQLException {
        String type = rs.getString("char_type");
        String name = rs.getString("name");
        int lv = rs.getInt("level");
        int hp = rs.getInt("hp");
        int atk = rs.getInt("attack_power");
        switch (type) {
            case "warrior": return new Warrior(name, lv, hp, atk, rs.getInt("defense_power"), rs.getString("weapon_type"));
            case "mage": return new Mage(name, lv, hp, atk, rs.getInt("mana"), rs.getInt("spell_power"));
            case "archer": return new Archer(name, lv, hp, atk, rs.getInt("arrow_count"), rs.getInt("range_val"));
            case "assassin": return new Assassin(name, lv, hp, atk, rs.getDouble("critical_rate"), rs.getInt("stealth_count"));
            case "priest": return new Priest(name, lv, hp, atk, rs.getInt("heal_power"), rs.getInt("faith_value"));
            default: throw new SQLException("未知类型");
        }
    }
}

// ==================== Swing 界面：登录 ====================
class LoginFrame extends JFrame {
    public LoginFrame() {
        setTitle("RPG 游戏角色管理系统 - 登录");
        setSize(400, 250);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setResizable(false);

        JPanel panel = new JPanel(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(10, 10, 10, 10);

        JTextField txtUser = new JTextField(15);
        JPasswordField txtPass = new JPasswordField(15);
        JButton btnLogin = new JButton("登录");
        JButton btnExit = new JButton("退出");

        gbc.gridx = 0; gbc.gridy = 0; panel.add(new JLabel("用户名："), gbc);
        gbc.gridx = 1; panel.add(txtUser, gbc);
        gbc.gridx = 0; gbc.gridy = 1; panel.add(new JLabel("密  码："), gbc);
        gbc.gridx = 1; panel.add(txtPass, gbc);

        JPanel btnPanel = new JPanel();
        btnPanel.add(btnLogin); btnPanel.add(btnExit);
        gbc.gridx = 0; gbc.gridy = 2; gbc.gridwidth = 2; panel.add(btnPanel, gbc);

        add(panel);

        btnLogin.addActionListener(e -> {
            String user = txtUser.getText().trim();
            String pass = new String(txtPass.getPassword());
            if ("admin".equals(user) && "123456".equals(pass)) {
                dispose();
                new MainFrame();
            } else {
                JOptionPane.showMessageDialog(this, "用户名或密码错误！", "登录失败", JOptionPane.ERROR_MESSAGE);
            }
        });

        btnExit.addActionListener(e -> System.exit(0));
        setVisible(true);
    }
}

// ==================== Swing 界面：主窗口 ====================
class MainFrame extends JFrame {
    private DefaultTableModel model;
    private CharacterDao dao = new CharacterDao();
    private JTextField txtSearch;

    public MainFrame() {
        setTitle("RPG 游戏角色管理系统");
        setSize(950, 600);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(EXIT_ON_CLOSE);

        // 北部查询
        JPanel topPanel = new JPanel();
        topPanel.add(new JLabel("按名称查询："));
        txtSearch = new JTextField(10);
        topPanel.add(txtSearch);
        JButton btnSearch = new JButton("查询");
        topPanel.add(btnSearch);
        topPanel.add(new JLabel("按类型筛选："));
        JComboBox<String> cmbType = new JComboBox<>(new String[]{"全部", "warrior", "mage", "archer", "assassin", "priest"});
        topPanel.add(cmbType);
        JButton btnFilter = new JButton("筛选");
        topPanel.add(btnFilter);
        add(topPanel, BorderLayout.NORTH);

        // 中部表格
        String[] cols = {"名称", "类型", "等级", "HP", "攻击", "专属属性1", "专属属性2"};
        model = new DefaultTableModel(cols, 0) {
            public boolean isCellEditable(int row, int column) { return false; }
        };
        JTable table = new JTable(model);
        table.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        table.setRowHeight(25);
        add(new JScrollPane(table), BorderLayout.CENTER);

        // 南部按钮
        JPanel bottomPanel = new JPanel();
        JButton btnAdd = new JButton("添加角色");
        JButton btnEdit = new JButton("修改角色");
        JButton btnDel = new JButton("删除角色");
        JButton btnAttack = new JButton("批量攻击");
        JButton btnLevel = new JButton("批量升级");
        JButton btnRefresh = new JButton("刷新");
        JButton btnExit = new JButton("退出");
        bottomPanel.add(btnAdd); bottomPanel.add(btnEdit); bottomPanel.add(btnDel);
        bottomPanel.add(btnAttack); bottomPanel.add(btnLevel); bottomPanel.add(btnRefresh); bottomPanel.add(btnExit);
        add(bottomPanel, BorderLayout.SOUTH);

        refreshTable();

        btnRefresh.addActionListener(e -> refreshTable());
        btnSearch.addActionListener(e -> {
            dao.findByName(txtSearch.getText().trim()).ifPresent(c -> {
                model.setRowCount(0);
                model.addRow(toRow(c));
            });
        });
        btnFilter.addActionListener(e -> {
            String type = (String) cmbType.getSelectedItem();
            if ("全部".equals(type)) refreshTable();
            else loadData(dao.findByType(type));
        });
        btnAdd.addActionListener(e -> new CharacterDialog(this, null, dao, this::refreshTable));
        btnEdit.addActionListener(e -> {
            int row = table.getSelectedRow();
            if (row < 0) { JOptionPane.showMessageDialog(this, "请选择一行"); return; }
            String name = (String) model.getValueAt(row, 0);
            dao.findByName(name).ifPresent(c -> new CharacterDialog(this, c, dao, this::refreshTable));
        });
        btnDel.addActionListener(e -> {
            int row = table.getSelectedRow();
            if (row < 0) { JOptionPane.showMessageDialog(this, "请选择一行"); return; }
            String name = (String) model.getValueAt(row, 0);
            if (JOptionPane.showConfirmDialog(this, "确定删除 " + name + " 吗？") == JOptionPane.YES_OPTION) {
                dao.deleteByName(name); refreshTable();
            }
        });
        btnAttack.addActionListener(e -> {
            StringBuilder sb = new StringBuilder("⚔️ 全体攻击结果：\n\n");
            for (GameCharacter c : dao.findAll()) {
                c.attack();
                sb.append(c.getInfo()).append("\n");
            }
            JOptionPane.showMessageDialog(this, sb.toString());
        });
        btnLevel.addActionListener(e -> {
            for (GameCharacter c : dao.findAll()) {
                c.levelUp();
                dao.update(c);
            }
            refreshTable();
            JOptionPane.showMessageDialog(this, "📈 全体升级完成！");
        });
        btnExit.addActionListener(e -> System.exit(0));

        setVisible(true);
    }

    public void refreshTable() { loadData(dao.findAll()); }

    private void loadData(List<GameCharacter> list) {
        model.setRowCount(0);
        for (GameCharacter c : list) model.addRow(toRow(c));
    }

    private Vector<Object> toRow(GameCharacter c) {
        Vector<Object> row = new Vector<>();
        row.add(c.getName());
        row.add(c.getClass().getSimpleName());
        row.add(c.getLevel());
        row.add(c.getHp());
        row.add(c.getAttackPower());
        if (c instanceof Warrior) {
            row.add("防御:" + ((Warrior)c).getDefensePower());
            row.add("武器:" + ((Warrior)c).getWeaponType());
        } else if (c instanceof Mage) {
            row.add("法力:" + ((Mage)c).getMana());
            row.add("法强:" + ((Mage)c).getSpellPower());
        } else if (c instanceof Archer) {
            row.add("箭矢:" + ((Archer)c).getArrowCount());
            row.add("射程:" + ((Archer)c).getRange());
        } else if (c instanceof Assassin) {
            row.add("暴击:" + (int)(((Assassin)c).getCriticalRate()*100) + "%");
            row.add("隐身:" + ((Assassin)c).getStealthCount());
        } else if (c instanceof Priest) {
            row.add("治疗:" + ((Priest)c).getHealPower());
            row.add("信仰:" + ((Priest)c).getFaithValue());
        } else { row.add("-"); row.add("-"); }
        return row;
    }
}

// ==================== Swing 界面：添加/修改对话框 ====================
class CharacterDialog extends JDialog {
    private CharacterDao dao;
    private Runnable onSuccess;
    private GameCharacter editing;

    private JTextField txtName = new JTextField(10);
    private JTextField txtLevel = new JTextField("1", 10);
    private JTextField txtHp = new JTextField("100", 10);
    private JTextField txtAtk = new JTextField("10", 10);
    private JComboBox<String> cmbType = new JComboBox<>(new String[]{"Warrior", "Mage", "Archer", "Assassin", "Priest"});

    private JTextField txtSpec1 = new JTextField(10);
    private JTextField txtSpec2 = new JTextField(10);
    private JLabel lblSpec1 = new JLabel("专属1");
    private JLabel lblSpec2 = new JLabel("专属2");

    public CharacterDialog(JFrame parent, GameCharacter c, CharacterDao dao, Runnable onSuccess) {
        super(parent, c == null ? "添加角色" : "修改角色", true);
        this.dao = dao; this.onSuccess = onSuccess; this.editing = c;
        setSize(400, 400);
        setLocationRelativeTo(parent);

        JPanel panel = new JPanel(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(5, 5, 5, 5);
        gbc.anchor = GridBagConstraints.WEST;

        int y = 0;
        addRow(panel, gbc, y++, "角色类型：", cmbType);
        addRow(panel, gbc, y++, "名称：", txtName);
        addRow(panel, gbc, y++, "等级：", txtLevel);
        addRow(panel, gbc, y++, "HP：", txtHp);
        addRow(panel, gbc, y++, "攻击：", txtAtk);
        addRow(panel, gbc, y++, lblSpec1, txtSpec1);
        addRow(panel, gbc, y++, lblSpec2, txtSpec2);

        if (c != null) {
            txtName.setText(c.getName()); txtName.setEditable(false);
            txtLevel.setText(String.valueOf(c.getLevel()));
            txtHp.setText(String.valueOf(c.getHp()));
            txtAtk.setText(String.valueOf(c.getAttackPower()));
            cmbType.setSelectedItem(c.getClass().getSimpleName());
            cmbType.setEnabled(false);
            if (c instanceof Warrior) {
                txtSpec1.setText(String.valueOf(((Warrior)c).getDefensePower()));
                txtSpec2.setText(((Warrior)c).getWeaponType());
            } else if (c instanceof Mage) {
                txtSpec1.setText(String.valueOf(((Mage)c).getMana()));
                txtSpec2.setText(String.valueOf(((Mage)c).getSpellPower()));
            } else if (c instanceof Archer) {
                txtSpec1.setText(String.valueOf(((Archer)c).getArrowCount()));
                txtSpec2.setText(String.valueOf(((Archer)c).getRange()));
            } else if (c instanceof Assassin) {
                txtSpec1.setText(String.valueOf(((Assassin)c).getCriticalRate()));
                txtSpec2.setText(String.valueOf(((Assassin)c).getStealthCount()));
            } else if (c instanceof Priest) {
                txtSpec1.setText(String.valueOf(((Priest)c).getHealPower()));
                txtSpec2.setText(String.valueOf(((Priest)c).getFaithValue()));
            }
        }

        cmbType.addActionListener(e -> updateLabels());

        JButton btnSave = new JButton("保存");
        JButton btnCancel = new JButton("取消");
        JPanel btnPanel = new JPanel();
        btnPanel.add(btnSave); btnPanel.add(btnCancel);
        gbc.gridx = 0; gbc.gridy = y; gbc.gridwidth = 2; gbc.anchor = GridBagConstraints.CENTER;
        panel.add(btnPanel, gbc);

        add(panel);
        updateLabels();

        btnSave.addActionListener(e -> save());
        btnCancel.addActionListener(e -> dispose());
        setVisible(true);
    }

    private void addRow(JPanel p, GridBagConstraints gbc, int y, String label, JComponent comp) {
        gbc.gridx = 0; gbc.gridy = y; gbc.gridwidth = 1;
        p.add(new JLabel(label), gbc);
        gbc.gridx = 1; p.add(comp, gbc);
    }
    private void addRow(JPanel p, GridBagConstraints gbc, int y, JLabel label, JComponent comp) {
        gbc.gridx = 0; gbc.gridy = y; gbc.gridwidth = 1;
        p.add(label, gbc);
        gbc.gridx = 1; p.add(comp, gbc);
    }

    private void updateLabels() {
        String type = (String) cmbType.getSelectedItem();
        switch (type) {
            case "Warrior": lblSpec1.setText("防御力："); lblSpec2.setText("武器："); break;
            case "Mage": lblSpec1.setText("法力："); lblSpec2.setText("法强："); break;
            case "Archer": lblSpec1.setText("箭矢："); lblSpec2.setText("射程："); break;
            case "Assassin": lblSpec1.setText("暴击率(0-1)："); lblSpec2.setText("隐身次数："); break;
            case "Priest": lblSpec1.setText("治疗量："); lblSpec2.setText("信仰值："); break;
        }
    }

    private void save() {
        try {
            String name = txtName.getText().trim();
            int lv = Integer.parseInt(txtLevel.getText());
            int hp = Integer.parseInt(txtHp.getText());
            int atk = Integer.parseInt(txtAtk.getText());
            String type = (String) cmbType.getSelectedItem();
            GameCharacter ch;
            switch (type) {
                case "Warrior": ch = new Warrior(name, lv, hp, atk, Integer.parseInt(txtSpec1.getText()), txtSpec2.getText()); break;
                case "Mage": ch = new Mage(name, lv, hp, atk, Integer.parseInt(txtSpec1.getText()), Integer.parseInt(txtSpec2.getText())); break;
                case "Archer": ch = new Archer(name, lv, hp, atk, Integer.parseInt(txtSpec1.getText()), Integer.parseInt(txtSpec2.getText())); break;
                case "Assassin": ch = new Assassin(name, lv, hp, atk, Double.parseDouble(txtSpec1.getText()), Integer.parseInt(txtSpec2.getText())); break;
                case "Priest": ch = new Priest(name, lv, hp, atk, Integer.parseInt(txtSpec1.getText()), Integer.parseInt(txtSpec2.getText())); break;
                default: throw new IllegalStateException("未知类型");
            }
            if (editing == null) dao.add(ch); else dao.update(ch);
            onSuccess.run();
            dispose();
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, "输入错误：" + ex.getMessage());
        }
    }
}
